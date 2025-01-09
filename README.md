# Signal Equalizer

### **Overview**
The Signal Equalizer is a desktop application developed to provide users with control over audio signals by allowing them to adjust the magnitudes of specific frequency components. This application is essential in the music and speech industries and serves biomedical applications, such as detecting hearing aid abnormalities. Users can interactively manipulate audio signals across different modes to meet specific audio processing needs.

---

### **Video Demo**
[Demo Video Link](https://github.com/user-attachments/assets/demo-video)

---

### **Features**

1. **Multiple Operation Modes**:
   - **Uniform Range Mode**: Divide the total frequency range of the input signal into 10 equal ranges of frequencies, each controlled by a dedicated slider.
   - **Musical Instruments and Animal Sounds Mode**: Adjust magnitudes of specific sounds in a mixture of at least four different musical instruments.
   - **Winner Filter Mode**: Apply advanced filtering techniques with a click of a button.
   - **Vowels Mode**: Control specific vowels or instruments within a song using sliders.

2. **Dynamic Slider Management**:
   - Each mode features sliders corresponding to frequency ranges relevant to the selected mode, offering flexible audio manipulation.

3. **Visual Spectrograms**:
   - Two spectrogram displays (input and output) that visually represent audio signals and update dynamically as sliders are adjusted.

4. **Cine Signal Viewers**:
   - Two linked viewers for synchronized play of input and output signals, equipped with controls such as play, stop, pause, speed control, zoom, and pan.

5. **Fourier Transform Visualization**:
   - Display the Fourier transform of the signal, with an option to switch between linear scale and Audiogram scale for detailed frequency analysis.

---

### **Application Interface**
Below are illustrative mockups of the application showcasing its key features (replace the placeholders with actual images):

1. **Main Interface with Equalizer Sliders**
   
   ![Screenshot main interface](https://github.com/user-attachments/assets/main-interface)

2. **Spectrogram Displays**
   
   ![Screenshot spectrograms](https://github.com/user-attachments/assets/spectrogram-display)

3. **Cine Signal Viewers**
   
   ![Screenshot cine viewers](https://github.com/user-attachments/assets/cine-viewers)

---

### **Setup and Installation**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/signal-equalizer.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd signal-equalizer
   ```
3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   python main.py
   ```

---

### **Usage Instructions**
1. Launch the application and select the desired mode from the options menu.
2. Use the sliders to adjust frequency components and observe changes in the output signal and spectrogram.
3. Utilize the cine signal viewers to synchronize and compare input and output audio signals in real time.
4. Switch between linear scale and Audiogram scale for the Fourier transform visualization as needed.

---

### **Credits**
- [Your Name](https://github.com/your-github-username)
- [Team Member 1](https://github.com/team-member1)
- [Team Member 2](https://github.com/team-member2)

---

### **Contact**
For any inquiries or feedback, please contact:
- **Name**: Your Name
- **Email**: [your.email@example.com](mailto:your.email@example.com)
