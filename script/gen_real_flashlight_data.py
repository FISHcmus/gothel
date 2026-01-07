from sqlalchemy.orm import Session

from model.Base import get_db
from model.FlashlightProblem import FlashlightProblemDB
from script.reset import reset_single_table


def create_real_flashlight_problems(session: Session) -> None:
    """
    Generate real flashlight drill problems for testing.

    Flashlight drills train rapid scanning and keyword location skills.
    Users must find and highlight the exact target text within a passage,
    typically under time pressure (15 seconds).
    """
    problems_data = [
        {
            "problem_statement": "Find the phrase 'climate change' in the passage",
            "target": "climate change",
            "reading_content": "Scientists have studied climate change for decades, collecting data from ice cores, tree rings, and ocean sediments. The evidence shows that Earth's temperature has risen by approximately 1.1°C since pre-industrial times. This warming trend is primarily driven by human activities, particularly the burning of fossil fuels which releases greenhouse gases into the atmosphere."
        },
        {
            "problem_statement": "Locate the number '1969' in the text",
            "target": "1969",
            "reading_content": "The Apollo 11 mission, launched on July 16, 1969, was a pivotal moment in human history. Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon's surface, while Michael Collins orbited above in the command module. Armstrong's famous words, 'That's one small step for man, one giant leap for mankind,' were broadcast to millions watching on Earth."
        },
        {
            "problem_statement": "Find the word 'photosynthesis' in the passage",
            "target": "photosynthesis",
            "reading_content": "Plants are remarkable organisms that produce their own food through a process called photosynthesis. Using chlorophyll in their leaves, they capture energy from sunlight and combine it with carbon dioxide from the air and water from the soil. This chemical reaction produces glucose, which the plant uses for energy and growth, while releasing oxygen as a byproduct."
        },
        {
            "problem_statement": "Locate the phrase 'artificial intelligence' in the text",
            "target": "artificial intelligence",
            "reading_content": "The development of artificial intelligence has transformed numerous industries over the past few decades. From healthcare diagnostics to autonomous vehicles, AI systems are becoming increasingly sophisticated. Machine learning algorithms can now recognize patterns in vast datasets, make predictions, and even generate creative content, raising important questions about the future of work and human-machine collaboration."
        },
        {
            "problem_statement": "Find the name 'Marie Curie' in the passage",
            "target": "Marie Curie",
            "reading_content": "Marie Curie was a pioneering physicist and chemist who conducted groundbreaking research on radioactivity. She was the first woman to win a Nobel Prize, the first person to win the award twice, and the only person to win Nobel Prizes in two different scientific fields. Her work with radium and polonium laid the foundation for modern nuclear physics and chemistry."
        },
        {
            "problem_statement": "Locate the phrase 'Renaissance period' in the text",
            "target": "Renaissance period",
            "reading_content": "The Renaissance period, spanning roughly from the 14th to the 17th century, marked a profound cultural rebirth in Europe. This era saw extraordinary achievements in art, literature, science, and philosophy. Artists like Leonardo da Vinci and Michelangelo created masterpieces that still inspire us today, while thinkers like Galileo challenged traditional views of the universe."
        },
        {
            "problem_statement": "Find the word 'biodiversity' in the passage",
            "target": "biodiversity",
            "reading_content": "Tropical rainforests are among the most biodiverse ecosystems on Earth, containing more than half of the world's plant and animal species. However, biodiversity in these vital habitats faces serious threats from deforestation, climate change, and illegal wildlife trade. Conservation efforts are essential to protect these irreplaceable ecosystems and the countless species they support."
        },
        {
            "problem_statement": "Locate the number '206' in the text",
            "target": "206",
            "reading_content": "The human skeletal system is a remarkable structure consisting of 206 bones in adults, though babies are born with approximately 270 bones that fuse together as they grow. These bones provide support, protect vital organs, enable movement through muscle attachment, and produce blood cells in the bone marrow. The skeleton also stores essential minerals like calcium and phosphorus."
        },
        {
            "problem_statement": "Find the phrase 'Great Wall of China' in the passage",
            "target": "Great Wall of China",
            "reading_content": "The Great Wall of China stretches over 13,000 miles across northern China, making it one of the most impressive architectural achievements in human history. Originally built to protect Chinese states from invasions, construction began as early as the 7th century BC. Today, it stands as a UNESCO World Heritage site and a powerful symbol of Chinese civilization."
        },
        {
            "problem_statement": "Locate the word 'democracy' in the text",
            "target": "democracy",
            "reading_content": "Ancient Athens is often credited as the birthplace of democracy, where citizens gathered in the assembly to debate and vote on important matters of state. While this early form of democracy was limited to free male citizens, excluding women, slaves, and foreigners, it established principles of citizen participation and rule by the people that continue to influence modern political systems worldwide."
        }
    ]

    for p_data in problems_data:
        # Check for duplicates by problem_statement
        exists = session.query(FlashlightProblemDB).filter(
            FlashlightProblemDB.problem_statement == p_data["problem_statement"]
        ).first()

        if not exists:
            problem = FlashlightProblemDB(
                problem_statement=p_data["problem_statement"],
                target=p_data["target"],
                reading_content=p_data["reading_content"]
            )
            session.add(problem)
            print(f"Added: {p_data['problem_statement']}")
        else:
            print(f"Skipped duplicate: {p_data['problem_statement']}")

    session.commit()
    print("Done generating real flashlight problems.")


if __name__ == "__main__":
    # Reset the table first
    reset_single_table("flashlight_problem_table")

    # Then get a fresh database session
    db_gen = get_db()
    db = next(db_gen)
    try:
        create_real_flashlight_problems(db)
    finally:
        db_gen.close()
