import json
import os
import re
from typing import Callable, Dict, Any

from logger_utils import console, log_step, log_thought, log_action, log_observation, log_final_answer
from prompts import build_messages

MAX_ITERATIONS = 10

# ---------------------------------------------------------------------------
# LLM backend helpers
# ---------------------------------------------------------------------------

def _call_ollama(model: str, system: str, user: str) -> str:
    import ollama
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        options={"temperature": 0.1, "num_predict": 4096},
    )
    return response["message"]["content"]


def _openai_compatible(url: str, api_key: str, model: str, system: str, user: str) -> str:
    import requests
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        },
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"{resp.status_code} {resp.reason}: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]


def _call_groq(model: str, system: str, user: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable not set.")
    return _openai_compatible("https://api.groq.com/openai/v1/chat/completions", api_key, model, system, user)


def _call_typhoon(model: str, system: str, user: str) -> str:
    api_key = os.environ.get("TYPHOON_API_KEY", "")
    if not api_key:
        raise RuntimeError("TYPHOON_API_KEY environment variable not set.")
    return _openai_compatible("https://api.opentyphoon.ai/v1/chat/completions", api_key, model, system, user)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class TravelAgent:
    def __init__(self, model_name: str = "typhoon-v2.5-30b-a3b-instruct", backend: str = "typhoon"):
        self.model_name = model_name
        self.backend = backend  # "ollama", "groq", or "typhoon"
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func

    def _call_llm(self, system: str, user: str) -> str:
        if self.backend == "groq":
            return _call_groq(self.model_name, system, user)
        if self.backend == "typhoon":
            return _call_typhoon(self.model_name, system, user)
        return _call_ollama(self.model_name, system, user)

    def _parse(self, text: str) -> Dict[str, Any]:
        result = {"thought": None, "action": None, "action_input": None, "final_answer": None}

        thought_m = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", text, re.DOTALL | re.IGNORECASE)
        if thought_m:
            result["thought"] = thought_m.group(1).strip()

        final_m = re.search(r"Final Answer:\s*(.+?)$", text, re.DOTALL | re.IGNORECASE)
        if final_m:
            result["final_answer"] = final_m.group(1).strip()
            return result

        action_m = re.search(r"Action:\s*(\w+)", text, re.IGNORECASE)
        if action_m:
            result["action"] = action_m.group(1).strip()

        input_m = re.search(r"Action Input:\s*(\{.+?\})", text, re.DOTALL | re.IGNORECASE)
        if input_m:
            raw = re.sub(r"\s+", " ", input_m.group(1).strip())
            try:
                result["action_input"] = json.loads(raw)
            except json.JSONDecodeError:
                result["action_input"] = {}

        return result

    def run(self, user_query: str) -> str:
        console.rule("[bold blue]Travel Planning Agent[/bold blue]")
        log_step("Query", user_query, "bold white")
        log_step("Backend", f"{self.backend} / {self.model_name}", "dim")

        history = ""

        for iteration in range(1, MAX_ITERATIONS + 1):
            log_step("Iteration", f"{iteration}/{MAX_ITERATIONS}", "dim")

            system_prompt, user_content = build_messages(user_query, history)

            try:
                llm_text = self._call_llm(system_prompt, user_content)
            except Exception as e:
                log_step("Error", f"LLM call failed: {e}", "red")
                return f"LLM error: {e}"

            parsed = self._parse(llm_text)

            if parsed["thought"]:
                log_thought(parsed["thought"])

            if parsed["final_answer"]:
                log_final_answer(parsed["final_answer"])
                return parsed["final_answer"]

            action = parsed.get("action")
            action_input = parsed.get("action_input") or {}

            if not action:
                log_step("Warning", "Could not parse an Action — stopping.", "red")
                return "Could not determine next action. Please rephrase your query."

            log_action(action, action_input)

            if action not in self.tools:
                observation = f"Unknown tool '{action}'. Available tools: {', '.join(self.tools)}"
            else:
                try:
                    observation = str(self.tools[action](**action_input))
                except TypeError as e:
                    observation = f"Tool '{action}' called with wrong arguments: {e}"
                except Exception as e:
                    observation = f"Tool '{action}' error: {e}"

            log_observation(observation)

            history += (
                f"Thought: {parsed['thought'] or ''}\n"
                f"Action: {action}\n"
                f"Action Input: {json.dumps(action_input)}\n"
                f"Observation: {observation}\n\n"
            )

        return "Reached maximum iterations without a final answer."

    def run_stream(self, user_query: str):
        """Generator version for Streamlit — yields step dicts instead of printing."""
        history = ""
        for iteration in range(1, MAX_ITERATIONS + 1):
            system_prompt, user_content = build_messages(user_query, history)
            try:
                llm_text = self._call_llm(system_prompt, user_content)
            except Exception as e:
                yield {"type": "error", "content": str(e)}
                return

            parsed = self._parse(llm_text)

            if parsed["thought"]:
                yield {"type": "thought", "content": parsed["thought"], "iteration": iteration}

            if parsed["final_answer"]:
                yield {"type": "final", "content": parsed["final_answer"]}
                return

            action = parsed.get("action")
            action_input = parsed.get("action_input") or {}

            if not action:
                yield {"type": "error", "content": "ไม่สามารถ parse action ได้"}
                return

            yield {"type": "action", "action": action, "input": action_input}

            if action not in self.tools:
                observation = f"ไม่พบ tool '{action}' มีแค่: {', '.join(self.tools)}"
            else:
                try:
                    observation = str(self.tools[action](**action_input))
                except TypeError as e:
                    observation = f"Tool arguments ผิด: {e}"
                except Exception as e:
                    observation = f"Tool error: {e}"

            yield {"type": "observation", "content": observation}

            history += (
                f"Thought: {parsed['thought'] or ''}\n"
                f"Action: {action}\n"
                f"Action Input: {json.dumps(action_input)}\n"
                f"Observation: {observation}\n\n"
            )

        yield {"type": "error", "content": "ครบ max iterations แล้วยังไม่ได้คำตอบ"}
