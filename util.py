def valid_input(prompt, acceptable_responses):
    response = input(prompt)
    if response in acceptable_responses:
        return response

    print("Invalid response. Expected", acceptable_responses)
    return valid_input(prompt, acceptable_responses)
