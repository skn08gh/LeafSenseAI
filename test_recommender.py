from plant_recommender import recommend_plants

results = recommend_plants(
    temperature=25,
    user_light="bright",
    humidity=60,
    soil_moisture="moderate"
)

print("\n🌱 PLANT RECOMMENDATIONS\n")

for plant in results:
    print(plant)