import streamlit as st

def show_popup():
    """
    Displays a pop-up message in the Streamlit app.
    """
    st.markdown("""
    <style>
    /* Pop-up container */
    .popup {
        display: block;  /* Changed from 'none' to 'block' */
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        text-align: center;
        max-width: 450px;
        font-family: Arial, sans-serif;
        animation: fadeIn 0.5s ease-in-out;
    }

    /* Overlay */
    .overlay {
        display: block;  /* Changed from 'none' to 'block' */
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }

    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Close button */
    .close-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        font-size: 22px;
        cursor: pointer;
        color: #999;
    }

    .close-btn:hover {
        color: #555;
    }

    /* Donate button */
    .donate-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        margin-top: 15px;
        transition: background-color 0.3s ease;
    }

    .donate-btn:hover {
        background-color: #45a049;
    }

    /* Subtle emphasis */
    .popup p strong {
        color: #4CAF50;
        font-weight: bold;
    }
    </style>

    <!-- Pop-up HTML -->
    <div class="overlay" id="overlay"></div>
    <div class="popup" id="popup">
        <button class="close-btn" onclick="closePopup()">×</button>
        <h2>Thank You for Downloading! 🎉</h2>
        <p>**"Efficiency is overrated. Value is what counts."**</p>
        <p>By downloading <strong>Code_File_Fusion</strong>, you've chosen to add value to your workflow—and that's no small feat.</p>
        <p>Did you find this tool useful? If yes, here's how you can turn your appreciation into action:</p>
        <ul style="list-style-type: none; padding: 0;">
            <li>☕ <strong>$5</strong>: A coffee to keep us coding.</li>
            <li>🛠️ <strong>$10</strong>: An hour of development (bug-free code, anyone?).</li>
            <li>🚀 <strong>$20+</strong>: Long-term project sustainability. You're building the future!</li>
        </ul>
        <a href="https://www.paypal.com/paypalme/justinduveen?" target="_blank">
            <button class="donate-btn">Support the Project 🚀</button>
        </a>
        <p><em>Your generosity fuels innovation. Every small action creates big change. Let’s build something amazing together!</em></p>
    </div>

    <script>
    // Function to show the pop-up
    function showPopup() {
        document.getElementById('overlay').style.display = 'block';
        document.getElementById('popup').style.display = 'block';
    }

    // Function to close the pop-up
    function closePopup() {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('popup').style.display = 'none';
    }

    // Show the pop-up immediately
    showPopup();
    </script>
    """, unsafe_allow_html=True)