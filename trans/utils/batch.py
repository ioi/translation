import cairo
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from pikepdf import Pdf
import pytz
import subprocess
from typing import List

from django.conf import settings

from trans.models import Translation, Contestant, Contest, User, UserContest
from trans.utils.pdf import POINTS_PER_MM, PAGE_WIDTH_POINTS, PAGE_HEIGHT_POINTS, SERIF_FONT, SANS_FONT



@dataclass
class RecipeContestant:
    recipe: 'BatchRecipe'
    contestant: Contestant
    translations: List[Translation] = field(default_factory=list)
    num_pages: List[int] = field(default_factory=list)

    def build_parts(self):
        page_counts = self.count_pages()
        parts = [self.build_banner_page(page_counts)]

        for trans, num_pages in zip(self.translations, page_counts):
            parts.append(trans.get_final_pdf_path())
            if settings.PRINT_BATCH_DUPLEX and num_pages % 2 != 0:
                parts.append(self.build_blank_page(trans))

        return parts

    def count_pages(self):
        page_counts = []
        for trans in self.translations:
            if settings.USE_CPDF:
                res = subprocess.run(['cpdf', '-pages', trans.get_final_pdf_path()], check=True, stdout=subprocess.PIPE)
                num_pages = int(res.stdout)
            else:
                with Pdf.open(trans.get_final_pdf_path()) as pdf:
                    num_pages = len(pdf.pages)
            page_counts.append(num_pages)
        return page_counts

    def build_banner_page(self, page_counts):
        banner_path = Path(settings.CACHE_DIR) / 'banner' / self.recipe.contest.slug
        banner_path.mkdir(parents=True, exist_ok=True)
        banner_pdf_path = banner_path / f'{self.contestant.code}.pdf'

        with cairo.PDFSurface(str(banner_pdf_path), PAGE_WIDTH_POINTS, PAGE_HEIGHT_POINTS) as surface:
            ctx = cairo.Context(surface)

            self.add_text(ctx,
                          PAGE_WIDTH_POINTS / 2, 20 * POINTS_PER_MM,
                          SANS_FONT, 28,
                          self.recipe.contest.title.upper(),
                          center=True)

            self.add_text(ctx,
                          PAGE_WIDTH_POINTS / 2, 50 * POINTS_PER_MM,
                          SANS_FONT, 40 * POINTS_PER_MM,
                          self.contestant.code,
                          bold=True,
                          center=True)

            if self.contestant.location != "":
                self.add_text(ctx,
                              PAGE_WIDTH_POINTS / 2, 100 * POINTS_PER_MM,
                              SANS_FONT, 20 * POINTS_PER_MM,
                              self.contestant.location,
                              bold=True,
                              center=True)

            if not self.recipe.user_contest.skip_verification:
                self.add_text(ctx,
                              PAGE_WIDTH_POINTS / 2, 130 * POINTS_PER_MM,
                              SANS_FONT, 20,
                              'CHECK WITH TEAM LEADER',
                              center=True)

            x = 20 * POINTS_PER_MM
            y = 160 * POINTS_PER_MM

            if self.translations:
                self.add_text(ctx, x, y, SERIF_FONT, 20, 'Envelope contents:')
                y += 45
                for trans, num_pages in zip(self.translations, page_counts):
                    pages = f'{num_pages} page{"s" if num_pages != 1 else ""}'
                    self.add_text(ctx,
                                  x + 20, y,
                                  SERIF_FONT, 20,
                                  f'• {trans.task.name} – {trans.user.language.name} ({trans.user.country.name}) – {pages}')
                    y += 30
            else:
                self.add_text(ctx,
                              x, y,
                              SERIF_FONT, 20,
                              'No translations requested.')

            self.add_text(ctx,
                          PAGE_WIDTH_POINTS / 2, PAGE_HEIGHT_POINTS - 15 * POINTS_PER_MM,
                          SERIF_FONT, 10,
                          self.recipe.when.strftime('%Y-%m-%d   %H:%M:%S'),
                          center=True)

            ctx.show_page()

            if settings.PRINT_BATCH_DUPLEX:
                ctx.show_page()

        return str(banner_pdf_path)

    def build_blank_page(self, trans):
        blank_path = Path(settings.CACHE_DIR) / 'blank' / self.recipe.contest.slug
        blank_path.mkdir(parents=True, exist_ok=True)
        blank_pdf_path = blank_path / f'{self.contestant.code}-{trans.task.name}.pdf'

        with cairo.PDFSurface(str(blank_pdf_path), PAGE_WIDTH_POINTS, PAGE_HEIGHT_POINTS) as surface:
            ctx = cairo.Context(surface)

            self.add_text(ctx,
                          PAGE_WIDTH_POINTS / 2, PAGE_HEIGHT_POINTS - 20 * POINTS_PER_MM,
                          SANS_FONT, 12,
                          f'Last page of {trans.task.name} for {self.contestant.code}',
                          center=True)

            self.add_text(ctx,
                          PAGE_WIDTH_POINTS / 2, PAGE_HEIGHT_POINTS / 3,
                          SERIF_FONT, 20,
                          'This page is intentionally blank.',
                          italic=True,
                          center=True)

        return str(blank_pdf_path)

    def add_text(self, ctx, x, y, font_face, font_size, text, center=False, bold=False, italic=False):
        ctx.select_font_face(font_face, int(italic), int(bold))
        ctx.set_font_size(font_size)
        if center:
            textents = ctx.text_extents(text)
            fextents = ctx.font_extents()
            y += fextents[0]
            ctx.move_to(x - textents.width / 2 - textents.x_bearing, y)
        else:
            ctx.move_to(x, y)
        ctx.show_text(text)


@dataclass
class BatchRecipe:
    contest: Contest
    for_user: User
    user_contest: UserContest
    ct_recipes: List[RecipeContestant] = field(default_factory=list)
    when: datetime = field(default_factory=lambda: datetime.now().astimezone(pytz.timezone(settings.TIME_ZONE)))

    def build_pdfs(self):
        if settings.PRINT_BATCH_WHOLE_TEAM:
            parts = []
            for ct_recipe in self.ct_recipes:
                parts.extend(ct_recipe.build_parts())
            pdfs = [self.build_batch(parts, self.for_user.username)]
        else:
            pdfs = []
            for ct_recipe in self.ct_recipes:
                pdf = self.build_batch(ct_recipe.build_parts(), f'{self.for_user.username}-{ct_recipe.contestant.code}')
                if pdf is not None:
                    pdfs.append(pdf)
        return pdfs

    def build_batch(self, parts, name_base):
        if not parts:
            return None

        output_path = Path(settings.MEDIA_ROOT) / 'batch' / str(self.contest.slug)
        output_path.mkdir(parents=True, exist_ok=True)
        output_pdf_path = output_path / f'{name_base}.pdf'
        if settings.USE_CPDF:
            cmd = ['cpdf'] + parts + ['-o', str(output_pdf_path)]
            subprocess.run(cmd, check=True)
        else:
            with Pdf.new() as output_pdf:
                for part in parts:
                    with Pdf.open(part) as part_pdf:
                        output_pdf.pages.extend(part_pdf.pages)
                output_pdf.save(output_pdf_path)

        return str(output_pdf_path)

    def add_contestant(self, contestant):
        ct_recipe = RecipeContestant(recipe=self, contestant=contestant)
        self.ct_recipes.append(ct_recipe)
        return ct_recipe
