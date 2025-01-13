# Signal Equalizer

## Overview  
Signal Equalizer is a versatile tool designed for audio and signal processing. It serves applications in music, speech processing, and biomedical fields such as hearing aid analysis and abnormalities detection. This desktop application allows users to modify the magnitudes of specific frequency components of a signal using sliders and then reconstruct the adjusted signal. The project includes multiple modes to cater to different use cases and provides intuitive visualization tools.

---

## Features  
- **Multiple Equalizer Modes:**
  1. **Uniform Range Mode**: Divides the frequency range into 10 equal segments, each controlled by a slider.  
  2. **Musical Instruments Mode**: Control specific instruments or animal sounds in a mixed audio file using dedicated sliders.  
  3. **Eliminates Vowels Mode**: Adjust or mute vowel components in songs using sliders.  
  4. **Wiener Filter Mode**: Remove noise from an audio file and reconstruct the clean signal.  

- **Interactive UI**:  
  - Switch seamlessly between modes by clicking on a button.  
  - Adjustable sliders dynamically update captions and counts per mode.  
  - Toggle frequency view between linear and audiogram scales.  

- **Visualization Tools**:  
  - Linked cine signal viewers for synchronous playback of input and output signals.  
  - Interactive features like play, pause, stop, speed control, zoom, pan, and reset.  
  - Spectrograms for input and output signals, updated dynamically with slider changes.  

---

## Video Demo  

https://github.com/user-attachments/assets/d9f477f2-027d-402d-b953-52c1aa925c3b


---

## Application Interface  

- ### **Uniform Range Mode**  
- **Hidden Spectrograms**
  ![image](https://github.com/user-attachments/assets/e843b1ce-948b-46ad-8fcd-2b6c7a5efd25)
  

- **Slider 2 and 3 are tunrning off range of frequrencies and reflecting on the output spectrogram**
- **The Audiogram Scale is displayed for visualization**
 ![image](https://github.com/user-attachments/assets/ef53bfa8-48b5-4c85-a8cd-8d4ac55529f0)

---

- ### **Hybrid Sounds Mode**  
- **Only the bird sound is audible as the sliders for all other frequencies are at minimum, effectively muting all other sounds.** 
  ![image](https://github.com/user-attachments/assets/6b1dc2cf-82fd-4c4b-9a6c-86da3f0f8498)

---

- ### **Eliminates Vowels Mode**  
   ![image](https://github.com/user-attachments/assets/ed7776e4-d70c-4848-b3d9-83d33db03882)
 
---

- ### **Wiener Filter Mode**  
- **After clicking on Adjust Band and eliminating the noise**
   ![image](https://github.com/user-attachments/assets/685132b5-29a3-478b-9fd0-efbef90e2e67)


---

## Setup and Installation  
### Prerequisites:  
- Python 3.8+  
- PyQt5  
- Numpy  
- Scipy  
- Matplotlib & PyQtGraph  
- Audio processing libraries like Librosa , sounddevice

### Installation:  
1. Clone this repository:  
   ```bash
   git clone https://github.com/madonna-mosaad/Signal-Equalizer.git
   cd Signal-Equalizer
### **Team Members**
This project wouldn’t have been possible without the hard work and collaboration of my amazing team. Huge shout-out to
- [Madonna Mosaad](https://github.com/madonna-mosaad)
- [Yassien Tawfik](https://github.com/YassienTawfikk)
- [Nancy Mahmoud](https://github.com/nancymahmoud1)

---

### **Contact**
For any inquiries or feedback, please contact:
- **Name**: Nancy Mahmoud
- **Email**: [Nancy.Abdelfattah03@eng-st.cu.edu.eg](mailto:nancy.abdelfattah03@eng-st.cu.edu.eg)
