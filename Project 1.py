''' This project is my first attempt at streamlit. What started off as a simple solution ended up becoming fairly complex for somebody with my level of understanding of streamlit (beginner), so 
it took me a fair amount of help from google, stackoverflow and PerplexityAI to develop the very first version, but since then I worked on understanding the various concepts and syntaxes, and then published 
the adapted and cleaner versions (including the one uploaded in this file) on my own, although I still have a fair way to go before being able to claim mastery of streamlit.

Problem statement: During my time at dots autonomous, we were in the course of developing a novel identification mechanism for autonomous vehicles. During the finetuning process, I realised that
our explanations and presentations were far too technical and relied too much on the audience understanding certain technical references, failing which nothing else would make sense.

Attempted solution: I developed a miniature web app using Streamlit that has an acceptably accurate portrayal of the novel mechanism. The UI allows even the most non-technical of audiences to 
develop a clear understanding of the working and logic, using buttons and click options to carry the audience along through the whole process. The app gives a live demonstration of how the mechanism adapts
to different inputs, with the final code changing as the user interacts with the different options available on the app. 

Libraries used: Primarily streamlit, with assistance from random, os, datetime, sys and subprocess. 

Updates in consideration: An AI voice-to-text converter that allows the user to simple speak the combination that they want displayed. The converter interprets the voice, converts it to text and passes 
it along to another (chatbot?) that then interprets the text input, adjusts the options and clickboxes accordingly, and finally outputs the expected ID code.
'''

import streamlit as st
import subprocess
import sys
import os
import random
from datetime import datetime

# Initialize session state for profile history (moved to top)
if 'profile_history' not in st.session_state:
    st.session_state.profile_history = []

def generate_profile(its, v2x_modes_dict, access_modes_dict):
    """
    Generate vehicle profile directly without subprocess
    
    Args:
        its: String - ITS provider name
        v2x_modes_dict: Dict - V2X mode selections {mode_name: boolean}
        access_modes_dict: Dict - Access mode selections {mode_name: boolean}
    
    Returns:
        String - Generated profile in format: ITS_CODE:V2X_PROFILE:HARDWARE_ID:ACCESS_SCOPE
    """
    
    its_list = {"Siemens": 1126, "Harman": 2852, "Schneider": 4389, "TATA": 1142, 
               "UMTC": 5374, "Huawei": 6782, "Kapsch": 3758, "Hitachi": 6820, 
               "GMV": 9903, "NEC": 1096}
    
    its_code = its_list[its]
    
    # V2X Profile Generation
    v2x_profile_bits = {"V2V":0, "V2I":1, "V2N":2, "V2P":3, "V2G":4, "V2D":5, "V2H":6, "RES":7}
    v2x_profile = ['0']*8
    
    for mode_name, is_enabled in v2x_modes_dict.items():
        if is_enabled and mode_name in v2x_profile_bits:
            v2x_profile[v2x_profile_bits[mode_name]] = "1"
    
    v2x_hex = f"{int(''.join(v2x_profile), 2):04X}"[2:]
    
    # Access Scope Generation
    access_scope_bits = {
        "READ_CAN":0, "WRITE_CAN":1, "BRAKE_CTRL":2, "STEER_CTRL":3,
        "POWERTRAIN_CTRL":4, "ADAS_ALERTS":5, "SENSOR_FEED":6, "VIDEO_STREAM":7,
        "AUDIO_STREAM":8, "NAV_DISPLAY":9, "HMI_NOTIF":10, "TELEMETRY_TX":11,
        "OTA_UPDATE":12, "DIAGNOSTICS":13, "HVAC_CTRL":14, "LIGHTS_CTRL":15
    }
    
    access_scope = ['0'] * 16
    
    for mode_name, is_enabled in access_modes_dict.items():
        if is_enabled and mode_name in access_scope_bits:
            access_scope[access_scope_bits[mode_name]] = "1"
    
    access_hex = f"{int(''.join(access_scope), 2):06X}"[2:]
    
    # Generate random hardware ID
    hardware_ID = f"{random.getrandbits(32):08X}"
    
    return f'{its_code}:{v2x_hex}:{hardware_ID}:{access_hex}'

# Configure page
st.set_page_config(
    page_title="Vehicle ITS Profile Generator",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Vehicle ITS Profile Generator")
st.markdown("Generate vehicle communication profiles for Intelligent Transportation Systems")

# Your existing data
its_list = {
    "Siemens": 1126, "Harman": 2852, "Schneider": 4389, "TATA": 1142, 
    "UMTC": 5374, "Huawei": 6782, "Kapsch": 3758, "Hitachi": 6820, 
    "GMV": 9903, "NEC": 1096
}

# Sidebar for quick info
st.sidebar.header("ℹ️ About")
st.sidebar.markdown("""
This tool generates vehicle communication profiles by:
1. Selecting an ITS provider (**Required**)
2. Choosing at least one V2X communication mode (**Required**)
3. Setting at least one system access permission (**Required**)
4. Running your Python script to generate the profile

⚠️ **All categories must have selections to generate a profile.**
""")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    # OEM Selection
    st.subheader("🏢 1. Select ITS Provider")
    selected_oem = st.selectbox(
        "Choose provider:",
        [""] + list(its_list.keys()),  # Add empty option
        help="Select the ITS (Intelligent Transportation Systems) provider"
    )
    
    # Show validation message for OEM
    if not selected_oem:
        st.warning("⚠️ Please select an ITS provider")
    
    # V2X Modes
    st.subheader("📡 2. V2X Communication Modes")
    st.markdown("*Select at least one communication mode*")
    
    v2x_col1, v2x_col2 = st.columns(2)
    
    with v2x_col1:
        v2v = st.checkbox("V2V", help="Vehicle-to-Vehicle communication")
        v2i = st.checkbox("V2I", help="Vehicle-to-Infrastructure communication")
        v2n = st.checkbox("V2N", help="Vehicle-to-Network communication") 
        v2p = st.checkbox("V2P", help="Vehicle-to-Pedestrian communication")
    
    with v2x_col2:
        v2g = st.checkbox("V2G", help="Vehicle-to-Grid communication")
        v2d = st.checkbox("V2D", help="Vehicle-to-Device communication")
        v2h = st.checkbox("V2H", help="Vehicle-to-Home communication")
        res = st.checkbox("RES", help="Reserved for future use")
    
    # Check if any V2X mode is selected
    v2x_selected = any([v2v, v2i, v2n, v2p, v2g, v2d, v2h, res])
    if not v2x_selected:
        st.warning("⚠️ Please select at least one V2X communication mode")

with col2:
    # Access Permissions
    st.subheader("🔐 3. System Access Permissions")
    st.markdown("*Select at least one access permission*")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Control", "🛡️ Safety", "📱 Media", "⚙️ Services"])
    
    with tab1:
        st.write("**CAN Bus Operations**")
        read_can = st.checkbox("Read CAN", help="Read from CAN bus")
        write_can = st.checkbox("Write CAN", help="Write to CAN bus")
        
        st.write("**Vehicle Control Systems**")
        brake_ctrl = st.checkbox("Brake Control", help="Control braking systems")
        steer_ctrl = st.checkbox("Steering Control", help="Control steering systems")
        powertrain_ctrl = st.checkbox("Powertrain Control", help="Control engine/motor systems")

    with tab2:
        st.write("**Safety Systems**")
        adas_alerts = st.checkbox("ADAS Alerts", help="Advanced Driver Assistance Systems alerts")
        sensor_feed = st.checkbox("Sensor Feed", help="Access to sensor data feeds")

    with tab3:
        st.write("**Media & Display**")
        video_stream = st.checkbox("Video Stream", help="Access to video streaming")
        audio_stream = st.checkbox("Audio Stream", help="Access to audio streaming")
        nav_display = st.checkbox("Navigation Display", help="Control navigation display")
        hmi_notif = st.checkbox("HMI Notifications", help="Human-Machine Interface notifications")

    with tab4:
        st.write("**Vehicle Services**")
        telemetry_tx = st.checkbox("Telemetry TX", help="Transmit telemetry data")
        ota_update = st.checkbox("OTA Updates", help="Over-The-Air software updates")
        diagnostics = st.checkbox("Diagnostics", help="Vehicle diagnostic access")
        hvac_ctrl = st.checkbox("HVAC Control", help="Climate control systems")
        lights_ctrl = st.checkbox("Lights Control", help="Vehicle lighting control")
    
    # Check if any access permission is selected
    access_selected = any([
        read_can, write_can, brake_ctrl, steer_ctrl, powertrain_ctrl,
        adas_alerts, sensor_feed, video_stream, audio_stream, nav_display,
        hmi_notif, telemetry_tx, ota_update, diagnostics, hvac_ctrl, lights_ctrl
    ])
    
    if not access_selected:
        st.warning("⚠️ Please select at least one system access permission")

# Generate Profile Section
st.subheader("🔧 4. Generate Profile")

# Validation check
all_requirements_met = selected_oem and v2x_selected and access_selected

# Show overall validation status
if not all_requirements_met:
    st.error("❌ **Cannot generate profile:** Please complete all required selections above")
    
    missing_items = []
    if not selected_oem:
        missing_items.append("• ITS Provider")
    if not v2x_selected:
        missing_items.append("• At least one V2X Communication Mode")
    if not access_selected:
        missing_items.append("• At least one System Access Permission")
    
    st.markdown("**Missing selections:**")
    for item in missing_items:
        st.markdown(item)
else:
    st.success("✅ All requirements met. Ready to generate profile!")

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    # Disable button if requirements not met
    generate_button = st.button(
        "🚀 Generate Profile", 
        type="primary", 
        use_container_width=True,
        disabled=not all_requirements_met,
        help="Complete all required selections to enable profile generation" if not all_requirements_met else "Generate your vehicle profile"
    )

# Only proceed if button clicked and all requirements met
if generate_button and all_requirements_met:
    with st.spinner('Generating profile...'):
        try:
            # Build mode dictionaries instead of subprocess arguments
            v2x_modes_dict = {
                "V2V": v2v,
                "V2I": v2i, 
                "V2N": v2n,
                "V2P": v2p,
                "V2G": v2g,
                "V2D": v2d,
                "V2H": v2h,
                "RES": res
            }
            
            access_modes_dict = {
                "READ_CAN": read_can,
                "WRITE_CAN": write_can,
                "BRAKE_CTRL": brake_ctrl,
                "STEER_CTRL": steer_ctrl,
                "POWERTRAIN_CTRL": powertrain_ctrl,
                "ADAS_ALERTS": adas_alerts,
                "SENSOR_FEED": sensor_feed,
                "VIDEO_STREAM": video_stream,
                "AUDIO_STREAM": audio_stream,
                "NAV_DISPLAY": nav_display,
                "HMI_NOTIF": hmi_notif,
                "TELEMETRY_TX": telemetry_tx,
                "OTA_UPDATE": ota_update,
                "DIAGNOSTICS": diagnostics,
                "HVAC_CTRL": hvac_ctrl,
                "LIGHTS_CTRL": lights_ctrl
            }
            
            # Call the function directly - no subprocess needed!
            profile = generate_profile(selected_oem, v2x_modes_dict, access_modes_dict)
            
            # ADD TO HISTORY HERE - profile is now defined and in scope!
            st.session_state.profile_history.append({
                'timestamp': datetime.now(),
                'oem': selected_oem,
                'profile': profile,
                'v2x_modes': [mode for mode, enabled in v2x_modes_dict.items() if enabled],
                'access_modes': [mode for mode, enabled in access_modes_dict.items() if enabled]
            })
            
            st.success("✅ Profile Generated Successfully!")
            
            # Display the full profile in a code block
            st.subheader("📄 Generated Profile")
            st.code(profile, language=None)
            
            # Parse and display breakdown
            profile_parts = profile.split(':')
            if len(profile_parts) == 4:
                st.subheader("📊 Profile Breakdown")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric(
                        label="🏢 ITS Code",
                        value=profile_parts[0],
                        help=f"Provider: {selected_oem}"
                    )
                
                with metric_col2:
                    st.metric(
                        label="📡 V2X Profile",
                        value=profile_parts[1],
                        help="Hexadecimal representation of V2X modes"
                    )
                
                with metric_col3:
                    st.metric(
                        label="🔧 Hardware ID",
                        value=profile_parts[2],
                        help="Random 32-bit hardware identifier"
                    )
                
                with metric_col4:
                    st.metric(
                        label="🔐 Access Scope",
                        value=profile_parts[3],
                        help="Hexadecimal representation of access permissions"
                    )
                    
                # Show active selections summary
                st.subheader("📋 Configuration Summary")
                
                summary_col1, summary_col2 = st.columns(2)
                
                with summary_col1:
                    st.write("**Active V2X Modes:**")
                    active_v2x = [mode for mode, enabled in v2x_modes_dict.items() if enabled]
                    
                    if active_v2x:
                        for mode in active_v2x:
                            st.write(f"• {mode}")
                    else:
                        st.write("None selected")
                
                with summary_col2:
                    st.write("**Active Access Permissions:**")
                    active_access = [mode for mode, enabled in access_modes_dict.items() if enabled]
                    
                    if active_access:
                        for access in active_access:
                            st.write(f"• {access.replace('_', ' ').title()}")
                    else:
                        st.write("None selected")
            
        except KeyError as e:
            st.error(f"❌ Invalid ITS provider selected: {e}")
        except Exception as e:
            st.error(f"❌ Error generating profile: {str(e)}")
            st.write(f"Error details: {type(e).__name__}")

elif generate_button and not all_requirements_met:
    # This should not happen due to disabled button, but just in case
    st.error("❌ Please complete all required selections before generating the profile.")

# Add a "Quick Select All" option
st.subheader("⚡ Quick Actions")
quick_col1, quick_col2, quick_col3 = st.columns(3)

with quick_col1:
    if st.button("✅ Select All V2X Modes"):
        st.rerun()

with quick_col2:
    if st.button("✅ Select All Access Permissions"):
        st.rerun()

with quick_col3:
    if st.button("🔄 Clear All Selections"):
        st.rerun()

# Profile History Section
if st.session_state.profile_history:
    st.subheader("📚 Profile History")
    
    # Show total count
    st.write(f"**Total profiles generated:** {len(st.session_state.profile_history)}")
    
    # Display recent profiles in an expander
    with st.expander(f"View {len(st.session_state.profile_history)} generated profiles"):
        for i, entry in enumerate(reversed(st.session_state.profile_history)):
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"**{entry['timestamp'].strftime('%H:%M:%S')}**")
                st.write(f"Provider: {entry['oem']}")
            
            with col2:
                st.code(entry['profile'], language=None)
            
            with col3:
                # Add download button for individual profiles
                st.download_button(
                    label="💾",
                    data=entry['profile'],
                    file_name=f"profile_{entry['oem']}_{entry['timestamp'].strftime('%H%M%S')}.txt",
                    mime="text/plain",
                    key=f"download_{i}",
                    help="Download this profile"
                )
            
            if i < len(st.session_state.profile_history) - 1:
                st.divider()
    
    # Clear history button
    if st.button("🗑️ Clear Profile History", type="secondary"):
        st.session_state.profile_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Vehicle ITS Profile Generator")
