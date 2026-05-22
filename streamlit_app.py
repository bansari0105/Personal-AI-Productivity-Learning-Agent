import streamlit as st
import requests
import json

st.set_page_config(page_title="Agentic AI", layout="wide")
st.title("Agentic AI Productivity Assistant")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("API URL", value="http://127.0.0.1:8000")

# Main tabs
tab1, tab2, tab3 = st.tabs(["Extract Tasks", "Schedule", "View Tasks"])

with tab1:
    st.header("Extract & Analyze Tasks")
    task_text = st.text_area("Describe your tasks:", placeholder="e.g., Go to gym and study ML")

    if st.button("Run the agent"):
        if task_text.strip():
            try:
                resp = requests.post(f"{api_url}/run-agent", json={"text": task_text})
                tasks = resp.json()

                st.success(f"Found {len(tasks)} task(s)")
                for task in tasks:
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Task:** {task['task']}")
                        with col2:
                            st.write(f"**Primary:** {task.get('category', 'N/A')}")
                        with col3:
                            conf = task.get('category_confidence', 0)
                            st.write(f"**Confidence:** {conf:.0%}")

                        # Show all detected categories
                        all_cats = task.get('all_categories', [])
                        if all_cats and len(all_cats) > 1:
                            st.write("**Also detected:**")
                            for cat_info in all_cats[1:]:  # Skip the primary one
                                st.write(f"  - {cat_info['category']} ({cat_info['confidence']:.0%})")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter some tasks first")

with tab2:
    st.header("Schedule tasks")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("Start time", value="09:00", placeholder="HH:mm")
    with col2:
        end_time = st.text_input("End time", value="17:00", placeholder="HH:mm")

    schedule_text = st.text_area("Tasks to schedule:", height=100)

    if st.button("Create Schedule"):
        if schedule_text.strip() and start_time and end_time:
            try:
                resp = requests.post(
                    f"{api_url}/schedule-tasks",
                    json={
                        "text": schedule_text,
                        "start_time": start_time,
                        "end_time": end_time
                    }
                )
                if resp.status_code == 200:
                    scheduled = resp.json()
                    st.success(f"Scheduled {len(scheduled)} task(s)")

                    for task in scheduled:
                        st.write(f"[{task.get('category', 'task')}] **{task['task']}** | {task['start']}-{task['end']} ({task.get('duration_minutes')} min)")
                else:
                    st.error(f"Error: {resp.json()}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all fields")

with tab3:
    st.header("Scheduled Tasks")

    if st.button("Refresh"):
        st.rerun()

    try:
        resp = requests.get(f"{api_url}/scheduled-tasks")
        tasks = resp.json()

        if tasks:
            st.write(f"**Total tasks: {len(tasks)}**")

            for task in tasks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"**{task['task']}**")
                    with col2:
                        st.write(f"{task['start']}-{task['end']}")
                    with col3:
                        st.write(f"{task.get('category', 'N/A')}")
                    with col4:
                        if st.button("Delete", key=f"del_{task.get('id')}"):
                            requests.delete(f"{api_url}/scheduled-tasks/{task.get('id')}")
                            st.rerun()
        else:
            st.info("No scheduled tasks yet")
    except Exception as e:
        st.error(f"Error: {e}")
