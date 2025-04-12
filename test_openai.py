import openai

openai.api_key = "sk-XXXXXXXXXXXXXXXXXXXXXXXX"  # paste your real key here

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say something sassy as Cardinal Carl about tacos"}
        ],
        temperature=0.9,
        max_tokens=60
    )

    print("✅ Success! Here's Carl's sass:")
    print(response.choices[0].message["content"])

except Exception as e:
    print("❌ Error:")
    print(e)
