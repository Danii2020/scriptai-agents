def build_prompt(agent_config: dict, input_vars: dict) -> str:
    prompt = f"""
        Role: {agent_config['role']}
        Goal: {agent_config['goal']}
        Backstory: {agent_config['backstory']}
    """
    for k, v in input_vars.items():
        prompt = prompt.replace(f'{{{k}}}', str(v))
    return prompt

def build_task_prompt(task_config: dict, input_vars: dict) -> str:
    prompt = f"""
        Task: {task_config['description']}
        Expected Output: {task_config['expected_output']}
    """
    for k, v in input_vars.items():
        prompt = prompt.replace(f'{{{k}}}', str(v))
    return prompt 