import prompts

def build_modules(model, config):
    output = []

    if config.get("daily_alpha", True):
        response = model.generate_content(prompts.DAILY_ALPHA)
        output.append(("🏆 DAILY SOLANA ALPHA", response.text))

    if config.get("meme", True):
        response = model.generate_content(prompts.MEME)
        output.append(("😂 MEME OF THE DAY", response.text))

    if config.get("gm", True):
        response = model.generate_content(prompts.GM)
        output.append(("☀️ GM LOAF GANG", response.text))

    return output
