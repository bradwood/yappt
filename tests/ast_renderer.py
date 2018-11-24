from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer

md = """**text to be strong** and not strong

* blah
* blah
  * blah blahblahblahblahblahblahblahblahblahblah blahblahblah *blahh* blahh blahh blahh blahh blahh blahh blahh blahh blahh blahh blahh blahh blah
  * blah


"""


with ASTRenderer() as renderer:
    rendered = renderer.render(Document(md))

print(rendered)
