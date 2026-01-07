import os
from fastapi import APIRouter, HTTPException
from starlette import status

from DTO.Assistant import AssistantRequestDTO, AssistantResponseDTO

# Lazy import OpenAI to avoid issues if not installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

router = APIRouter(prefix="/assistant")

# Lazy initialization of OpenAI client
_openai_client = None


def get_openai_client():
    """Get or initialize OpenAI client"""
    global _openai_client

    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API key not configured"
            )

        if OpenAI is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI library not installed"
            )

        _openai_client = OpenAI(api_key=api_key)

    return _openai_client


def get_emotion_for_situation(situation: str) -> str:
    """Map situation to emotion state"""
    emotion_map = {
        'wrong_evidence': 'thinking',
        'stuck': 'thinking',
        'wrong_answer': 'concerned'
    }
    return emotion_map.get(situation, 'idle')


@router.post("/suggest", response_model=AssistantResponseDTO)
async def get_suggestion(request: AssistantRequestDTO):
    """
    Get AI-powered suggestion for student based on their situation.

    Uses OpenAI GPT-4o-mini to generate contextual hints.
    """
    # System prompt
    system_prompt = """You are a helpful IELTS reading practice assistant. Your role is to provide brief, encouraging guidance to students when they make mistakes.

Guidelines:
- Keep responses under 40 words
- Be encouraging and supportive, never discouraging
- Provide specific, actionable hints based on what they selected
- Point out what to look for without giving the answer
- Reference specific keywords or concepts from the text
- Help them develop critical thinking skills"""

    # Build user prompt based on situation
    user_prompt = ""

    if request.situation == 'wrong_evidence':
        user_prompt = f"""The student is trying to answer: "{request.problemStatement}"

They highlighted this text: "{request.userSelectedText}"

But this is incorrect. The correct evidence is somewhere else in this passage:
\"\"\"
{request.readingContent}
\"\"\"

The correct evidence contains: "{request.correctEvidence}"

Help them understand:
1. Why their selection doesn't answer the question
2. What keywords from the question they should look for
3. What part of the passage might contain the answer

Keep it brief but specific to their mistake."""

    elif request.situation == 'wrong_answer':
        user_prompt = f"""The student selected: "{request.options[request.userAnswer]}"

But the correct answer is: "{request.options[request.correctAnswer]}"

Here's the evidence they found: "{request.correctEvidence}"

The full reading passage:
\"\"\"
{request.readingContent}
\"\"\"

Help them understand:
1. Why their selected answer doesn't match the evidence
2. What the evidence actually says
3. How to better interpret the evidence

Be specific about the mismatch between what they chose and what the evidence says."""

    elif request.situation == 'stuck':
        user_prompt = f"""The student seems stuck on: "{request.problemStatement}"

Reading passage:
\"\"\"
{request.readingContent}
\"\"\"

Give them a gentle hint:
1. What keywords to look for
2. What section of the passage might help
3. What strategy to use (scanning, careful reading, etc.)

Keep it encouraging and actionable."""

    # Fallback messages if OpenAI fails
    fallback_messages = {
        'wrong_evidence': "That selection doesn't seem to answer the question. Look for specific keywords from the question in the passage.",
        'wrong_answer': "Not quite right. Compare your answer carefully with what the evidence actually says.",
        'stuck': "Take your time. Try scanning for keywords from the question, then read that section carefully."
    }

    try:
        # Get OpenAI client
        client = get_openai_client()

        # Call OpenAI API (synchronous call)
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=0.7,
            max_tokens=150,
        )

        suggestion = completion.choices[0].message.content or 'Keep trying! You can do this!'

        return AssistantResponseDTO(
            suggestion=suggestion,
            emotion=get_emotion_for_situation(request.situation)
        )

    except HTTPException:
        # Re-raise HTTP exceptions (API key not configured, etc.)
        raise

    except Exception as e:
        # Log error and return fallback
        print(f"OpenAI API error: {str(e)}")

        return AssistantResponseDTO(
            suggestion=fallback_messages.get(request.situation, "Keep going! You're doing great!"),
            emotion=get_emotion_for_situation(request.situation)
        )
