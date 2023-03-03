import repvis

if __name__ == "__main__":
    descriptive_stats = repvis.HTMLTemplatedDocument("body_variable",
                                                     repvis.MarkdownVisElement("#Descriptive Statistics\n"
                                                                               "This section provides a drill down aspect to the result set.\n"
                                                                               "# Papers per institute\n-----\n\n-----\n\n-----\n\n-----"),
                                                     "basic_html_report.html", 
                                                     "descstats.html")

    descriptive_stats.render()
