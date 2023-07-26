import freetype

class CharacterSlot:
    def __init__(self, texture, glyph):
        self.texture = texture
        self.ascender  = glyph.bitmap_top
        self.descender = glyph.bitmap.rows-glyph.bitmap_top
        self.textureSize = (max(0, glyph.bitmap.width), self.ascender + self.descender)

        if isinstance(glyph, freetype.GlyphSlot):
            self.bearing = (glyph.bitmap_left, glyph.bitmap_top)
            self.advance = glyph.advance.x
        elif isinstance(glyph, freetype.BitmapGlyph):
            self.bearing = (glyph.left, glyph.top)
            self.advance = None
        else:
            raise RuntimeError('unknown glyph type')
