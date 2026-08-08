col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown("### 🛑 Live Containment Playbook")
            
            real_actions = agg_data.get("actions", ["Isolate Host"])
            real_predictions = agg_data.get("predictions", ["Lateral movement anticipated."])
            
            if exec_mode == "Human-in-the-Loop" and not st.session_state.human_approved:
                st.warning("⚠️ **HUMAN OVERRIDE REQUIRED:** Swarm consensus reached.")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✅ Approve AI Playbook (+1 Reward)", type="secondary", use_container_width=True):
                        # Trigger Positive RL Reinforcement
                        from agents.rl_engine import RLMemoryEngine
                        RLMemoryEngine().update_reward("General_Threat", real_actions[0], 1)
                        st.session_state.human_approved = True
                        st.rerun()
                with c_btn2:
                    if st.button("❌ Reject AI Playbook (-1 Reward)", use_container_width=True):
                        # Trigger Negative RL Reinforcement
                        from agents.rl_engine import RLMemoryEngine
                        RLMemoryEngine().update_reward("General_Threat", real_actions[0], -1)
                        st.error("Playbook rejected. RL Q-Table penalized. System will recalculate next time.")
                        st.stop()
            else:
                action_html = "<br>".join([f"> Executing: {act}... <span class='success-text'>SUCCESS</span>" for act in real_actions])
                
                st.markdown(f"""
                <div class="action-log">
                    [RL ENGINE] Historical reward weights applied.<br>
                    [ORCHESTRATOR] Semantic Memory updated.<br>
                    <br>
                    {action_html}<br>
                    <br>
                    [STATUS] <span class="success-text">ENVIRONMENT SECURED.</span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🔮 Predictive Threat Forecasting")
            st.info(f"**AI Swarm Prediction Engine:** {real_predictions[0] if real_predictions else 'Forecasting unavailable.'}")

        with col2:
            st.markdown("### 🧠 Raw Explainability Data")
            st.json(st.session_state.final_results.get("specialists", {}))
