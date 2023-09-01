from docvis.docs import Page, Document

if __name__ == "__main__":
    ip1 = Page("index",
               "# Index\n\n1. This is the index page\n\n* {{link_to_element('Subdoc','main/subdoc/index')}}\n* {{link_to_element('Page 1','main/subdoc/p1')}}\n* {{link_to_element('Page 2','main/subdoc/p2')}}",
               {},)
    p1 = Page("p1",
              "# Page 1\n\nThis is page1\n\n{{link_to_element('Back to index','main/subdoc/index')}}",
              {})
    p2 = Page("p2",
              "# Page 2\n\nThis is page 2\n\n{{link_to_element('Back to index','main/subdoc/index')}}\n\n{{link_to_element('Back to main index','main/index')}}",
              {})

    d2 = Document("subdoc",
                  Page("index",
                       "# Index for subdoc\n\nThis is the index page for subdoc\n\n {{link_to_element('Back to main index', 'main/index')}}",
                       {},),
                  [
                      p1,
                      p2
                  ])

    d1 = Document("main",
                 ip1,
                 [
                     d2,
                     Page("dummy", "# Something something",{})
                 ])
    d1.render()

