from docvis.docs import Page, Document

if __name__ == "__main__":
    d1 = Document("main",
                  [
                      Page("index",
                           "# This is the main document\n\n1. {{link_to_element('Page 1','main/p1')}}\n2. {{link_to_element('Page 2','main/p2')}}\n3. {{link_to_element('Other','main/subdoc/p1')}}",
                           {}),
                      Page("p1",
                           "# This is page 1\n\n{{link_to_element('Main','main/index')}}",
                           {}),
                      Page("p2",
                           "# This is page 2\n\n{{link_to_element('Main','main/index')}}",
                           {}),
                      Document("subdoc",[
                                         Page("p1",
                                              "# Subdoc's page 1\n\n{{link_to_element('To page 2','main/subdoc/p2')}}",
                                              {}),
                                         Page("p2",
                                             "# Subdoc's Page 2\n\n{{link_to_element('Back to main','main/index')}}\n\n\n",
                                             {})
                                        ])
                  ])
    d1.render()

