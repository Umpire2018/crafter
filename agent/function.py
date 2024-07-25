async def original_agentless_method():
    from agent.gitignore_matcher import GitIgnoreMatcher
    from agent.directory_tree_printer import DirectoryTreePrinter
    from agent.constans import obtain_relevant_files_prompt
    from agent.github_issues_client import GitHubIssuesClient
    from llama_index.core import PromptTemplate

    gitignore_path = ".gitignore"  
    matcher = GitIgnoreMatcher(gitignore_path)

    directory_to_check = ("RepoAgent" )
    language = "python"

    not_ignored_files = matcher.check_directory(directory_to_check, language)

    tree_printer = DirectoryTreePrinter(directory_to_check, target_language=language)
    
    tree_string = tree_printer.generate_tree_string(not_ignored_files) 
    qa_template = PromptTemplate(obtain_relevant_files_prompt)
    github_issue_client = GitHubIssuesClient()
    problem_statement = await github_issue_client.get_issue_description(owner="OpenBMB", repo="RepoAgent", issue_number=70)

    prompt = qa_template.format(problem_statement=problem_statement, structure=tree_string)
    initializer = LLMInitializer()

    llm = await initializer.initialize()


    resp = await llm.astream_complete(prompt)
    
    raw_contents = []

    async for r in resp:
        print(r.delta, end="", flush=True)
        raw_contents.append(r.raw)
        if r.raw.get('done'):
            LLMInitializer.print_final_response_details(r.raw)