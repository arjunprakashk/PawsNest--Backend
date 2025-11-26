# myapp/views_chatbot.py
from django.http import JsonResponse
from django.db.models import Q
from myapp.models import Pet
import requests, json, re
import os

# 🔑 Groq API Config
GROQ_TOKEN = os.getenv("GROQ_TOKEN")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def chatbot_response(request):
    user_message = request.GET.get("message", "").lower().strip()
    if not user_message:
        return JsonResponse({"reply": "Please type something!"})

    # 🐾 Check if user is asking about pets/adoption
    keywords = ["dog", "cat", "pet", "adopt", "animals", "puppy", "kitten"]
    if any(word in user_message for word in keywords):
        pets = Pet.objects.filter(is_adopted=False)

        # 🐕 Filter by breed/species words
        if "dog" in user_message or "puppy" in user_message:
            pets = pets.filter(Q(breed__icontains="dog") | Q(breed__icontains="puppy"))
        elif "cat" in user_message or "kitten" in user_message:
            pets = pets.filter(Q(breed__icontains="cat") | Q(breed__icontains="kitten"))

        # ⚧ Gender filter
        if "male" in user_message:
            pets = pets.filter(gender__iexact="Male")
        elif "female" in user_message:
            pets = pets.filter(gender__iexact="Female")

        # 📏 Size filter
        for size in ["small", "medium", "large"]:
            if size in user_message:
                pets = pets.filter(size__iexact=size.capitalize())

        # 👶 Age filter (detect "under 2 years", "below 3", etc.)
        match = re.search(r"(?:under|below|less than)\s*(\d+)", user_message)
        if match:
            limit = int(match.group(1))
            pets = [p for p in pets if _convert_age(p.age) < limit]

        # 🐾 Prepare structured data for frontend
        pet_data = []
        for p in pets[:6]:
            pet_data.append({
                "id": p.id,
                "name": p.name,
                "breed": p.breed,
                "gender": p.gender,
                "age": p.age,
                "size": p.size,
                "location": p.location,
                "image": p.image.url if p.image else None,
                "detail_url": f"/pets/{p.id}/"  # 👈 adjust to match your React route
            })

        # 🧾 If no pets found, show top 5 available
        if not pet_data:
            top_pets = Pet.objects.filter(is_adopted=False)[:5]
            if top_pets.exists():
                pet_data = [{
                    "id": p.id,
                    "name": p.name,
                    "breed": p.breed,
                    "gender": p.gender,
                    "age": p.age,
                    "size": p.size,
                    "location": p.location,
                    "image": p.image.url if p.image else None,
                    "detail_url": f"/pets/{p.id}/"
                } for p in top_pets]
                reply = "I couldn’t find an exact match, but here are some other adorable pets for adoption 🐾:"
            else:
                return JsonResponse({"reply": "No pets are currently available 🐶🐱."})
        else:
            reply = f"I found {len(pet_data)} pets that match your search 🐾."

        return JsonResponse({"reply": reply, "pets": pet_data})

    # 💬 Otherwise, use Groq AI for general chat
    headers = {"Authorization": f"Bearer {GROQ_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are PawsNestBot 🐾, a helpful and friendly pet adoption assistant."},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, data=json.dumps(payload), timeout=60)
        if r.status_code != 200:
            return JsonResponse({"reply": f"⚠️ Groq Error {r.status_code}: {r.text}"})
        data = r.json()
        reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"Error: {e}"

    return JsonResponse({"reply": reply})


# 🧮 Helper: convert "2 years" or "8 months" → float
def _convert_age(age_str):
    try:
        s = age_str.lower()
        if "month" in s:
            num = float(re.findall(r"\d+", s)[0]) / 12
        elif "year" in s:
            num = float(re.findall(r"\d+", s)[0])
        else:
            num = float(re.findall(r"\d+", s)[0])
        return num
    except:
        return 0
