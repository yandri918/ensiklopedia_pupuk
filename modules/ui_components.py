import streamlit as st

def render_fertilizer_card(item):
    """Render a card for fertilizer details."""
    with st.container():
        st.subheader(f"{item['name']}")
        st.caption(f"Type: {item['type']} | Category: {item['category']}")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"**Description:** {item['description']}")
            
            st.markdown("**Functions:**")
            for f in item['functions']:
                st.markdown(f"- {f}")
                
            st.info(f"💡 **Application Guide:** {item['application_guide']}")
            
        with c2:
            st.markdown("**Nutrient Content:**")
            for n, v in item['nutrient_content'].items():
                st.metric(n, v)
        
        st.warning(f"⚠️ **Precautions:** {item.get('precautions', 'None')}")
        st.markdown(f"*References: {', '.join(item.get('references', []))}*")
        st.markdown("---")

def render_pesticide_card(item):
    """Render a card for pesticide details."""
    colors = {
        "Kelas U": "green", "Kelas III": "blue", 
        "Kelas II": "orange", "Kelas I": "red"
    }
    safety = item.get('safety_level', 'Unknown')
    color = "grey"
    for k, v in colors.items():
        if k in safety: color = v
            
    with st.container():
        st.subheader(f"{item['name']}")
        st.caption(f"Target: {item['target']} | Active: {item['active_ingredient']}")
        
        st.markdown(f"<span style='background-color:{color}; color:white; padding:4px 8px; border-radius:4px;'>{safety}</span>", unsafe_allow_html=True)
        st.markdown("")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Mode of Action:** {item['mode_of_action']}")
            st.markdown(f"**Description:** {item['description']}")
            st.info(f"🎯 **Target Pests:** {', '.join(item.get('target_pests', []))}")
            
        with c2:
            st.markdown(f"**Application Guide:** {item['application_guide']}")
            st.warning(f"⚠️ **Precautions:** {item.get('precautions', '-')}")
            
        st.markdown(f"*References: {', '.join(item.get('references', []))}*")
        st.markdown("---")
