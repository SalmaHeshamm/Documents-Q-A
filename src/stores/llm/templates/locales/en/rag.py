from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template("\n".join([
    "You are an assistant that generates responses for the user.",
    "You will be provided with a set of documents related to the user's query.",
    "You have to generate a response based on the provided documents.",
    "Ignore any documents that are not relevant to the user's query.",
    "You may apologize to the user if you are unable to generate a response.",
    "You have to generate the response in the same language as the user's query.",
    "Be polite and respectful to the user.",
    "Be precise and concise in your response. Avoid unnecessary information."
]))

#### Document #####

document_prompt = Template("\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text"
]))


#### Footer ####

footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the user.",
    "## Question:",
    "$query",
    "",
    "## Answer:"
]))
