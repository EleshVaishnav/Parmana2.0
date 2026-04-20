from .registry import registry
import datetime
import threading
import time
import json
import uuid
import Memory.vector_memory as vm
from Core.logger import logger

# Try to fetch current active agent globally or we can pass notification indirectly.
# But since hook is on DeepClawAgent, we need a way to reach it. 
# We'll just define a global hook that main.py or agent.py can attach to.
global_notification_hook = None
_current_agent_ref = None  # Set by agent.py so schedule_action can get the real sender ID

def _reminder_daemon():
    """Background thread that constantly checks ChromaDB for ripe reminders."""
    logger.info("[SCHEDULER] Reminder daemon thread started.")
    print("[SCHEDULER] ✅ Reminder daemon is running (checking every 10s).")
    
    while True:
        try:
            if vm.vector_memory:
                results = vm.vector_memory.get_reminders()
                
                if results and "ids" in results and len(results["ids"]) > 0:
                    logger.info(f"[SCHEDULER] Found {len(results['ids'])} pending reminder(s).")
                    
                    for i in range(len(results["ids"])):
                        doc_id = results["ids"][i]
                        meta = results["metadatas"][i]
                        doc = results["documents"][i]
                        
                        execute_at_str = meta.get("execute_at")
                        target_user = meta.get("target_user")
                        
                        if execute_at_str and target_user:
                            try:
                                execute_at = datetime.datetime.fromisoformat(execute_at_str)
                                now = datetime.datetime.now()
                                
                                if now >= execute_at:
                                    # FIRE NOTIFICATION!
                                    logger.info(f"[SCHEDULER] 🔔 FIRING reminder to '{target_user}': {doc}")
                                    print(f"\n[SCHEDULER] 🔔 FIRING reminder to '{target_user}': {doc}")
                                    
                                    if global_notification_hook:
                                        global_notification_hook(target_user, f"⏰ Reminder: {doc}")
                                        logger.info(f"[SCHEDULER] ✅ Notification sent successfully.")
                                    else:
                                        logger.warning("[SCHEDULER] ⚠️ No notification hook configured! Reminder fired but nobody is listening.")
                                        print("[SCHEDULER] ⚠️ No notification hook configured! Reminder fired but nobody is listening.")
                                        
                                    # DELETE FROM MEMORY after firing
                                    vm.vector_memory.delete_memory(doc_id)
                                    logger.info(f"[SCHEDULER] Cleaned up reminder {doc_id} from DB.")
                                else:
                                    diff = (execute_at - now).total_seconds()
                                    logger.info(f"[SCHEDULER] Reminder '{doc}' fires in {diff:.0f}s (at {execute_at_str})")
                                    
                            except Exception as e:
                                logger.error(f"[SCHEDULER] Error processing reminder {doc_id}: {e}")
                                print(f"[SCHEDULER] Error processing reminder {doc_id}: {e}")
                        else:
                            logger.warning(f"[SCHEDULER] Reminder {doc_id} missing execute_at or target_user: {meta}")
                                
        except Exception as e:
            logger.error(f"[SCHEDULER] Daemon error: {e}")
            print(f"[SCHEDULER] Daemon error: {e}")
            
        time.sleep(10) # Check every 10 seconds

# Start daemon thread immediately upon import
threading.Thread(target=_reminder_daemon, daemon=True, name="ReminderDaemon").start()


@registry.register(
    name="schedule_action",
    description="Schedules a proactive message/reminder to be sent to a user at a specific future ISO format time.",
    parameters={
        "action_description": {"type": "string", "description": "What to remind the user about"},
        "time_iso": {"type": "string", "description": "Time in strictly ISO format, e.g. 2026-04-11T15:30:00"},
        "target_user_id": {"type": "string", "description": "The exact user ID to send the reminder to (find this in your context)"}
    }
)
def schedule_action(action_description: str, time_iso: str, target_user_id: str) -> str:
    try:
        # Validate format
        dt = datetime.datetime.fromisoformat(time_iso)
        
        if not vm.vector_memory:
            return "Scheduler Error: Persistent vector memory is not initialized yet."
        
        # CRITICAL: Override the LLM's hallucinated user ID with the real one
        # The agent tracks the actual sender_id from the current conversation
        real_user_id = target_user_id  # fallback to whatever LLM provided
        
        # Use the global reference set by the agent
        if _current_agent_ref and hasattr(_current_agent_ref, 'current_sender_id') and _current_agent_ref.current_sender_id:
            real_user_id = _current_agent_ref.current_sender_id
            logger.info(f"[SCHEDULER] Overriding LLM user ID '{target_user_id}' with real sender: '{real_user_id}'")
            
        # Bind into ChromaDB with explicit "type": "reminder"
        doc_id = str(uuid.uuid4())
        vm.vector_memory.add_memory(
            text=action_description,
            metadata={
                "type": "reminder",
                "execute_at": time_iso,
                "target_user": real_user_id
            },
            memory_id=doc_id
        )
        
        return f"Successfully scheduled reminder for {real_user_id} at {dt} (Stored persistently in ChromaDB)."
    except ValueError:
        return "Schedule Error: Ensure time_iso is strictly in ISO format (e.g. 2026-04-11T15:30:00)."
    except Exception as e:
        return f"Schedule Error: {str(e)}"

