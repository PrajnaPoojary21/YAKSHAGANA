def generate_story(summary_text):
    """
    Takes the matched padya's summary text (already written, from the
    curated dataset) and returns it as the final story output.

    No LLM call here by design: the dataset itself is the source of
    truth for the narrative meaning, and passing it through an external
    model would dilute the value of the dataset that was built for
    this project. This function only handles light formatting/cleanup.
    """
    if not summary_text:
        return ""

    # Basic cleanup: normalize whitespace, strip stray leading/trailing
    # blank lines that can come from multi-paragraph cells in the sheet.
    lines = [line.strip() for line in summary_text.strip().splitlines()]
    lines = [line for line in lines if line]  # drop empty lines

    story = "\n\n".join(lines)
    return story