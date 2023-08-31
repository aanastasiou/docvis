from docvis.docs import Page, Document

if __name__ == "__main__":
    ip1 = Page("index",
               "# Index\n\n1. This is the index page\n\n{{link_to_element('blah','p1')}}",
               {},)
    p1 = Page("p1",
              "# Page 1\n\nThis is page1\n\n{{link_to_element('Back to index','index')}}",
              {})
    q = Document("main",
                 ip1,
                 [
                     p1,
                 ])
    q.render()

