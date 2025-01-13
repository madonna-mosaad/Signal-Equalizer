import sys
import warnings
import numpy as np

# PyQt5 imports
from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

# PyQtGraph imports
import pyqtgraph as pg
from pyqtgraph import PlotWidget, mkPen

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# SciPy imports
from scipy.fft import rfft, rfftfreq, irfft
from scipy.signal import spectrogram

# Librosa import
import librosa

# SoundDevice import
import sounddevice as sd

# Application-specific imports
import app.wiener_filter.Wiener as nr
from app.ui.Design import Ui_MainWindow
from app.utils.clean_cache import remove_directories

# Ignore specific runtime warnings related to overflow in casting
warnings.filterwarnings('ignore', 'overflow encountered in cast')


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.is_toggle = False

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize widgets and variables
        self.init_graph_widgets()
        self.setup_signals()  # Connect template signals to functions
        self.initialize_playback()  # Initialize playback variables

        # Modes setup
        self.modes = ["Uniform Range", "Hybrid Sounds", "Eliminates Vowels", "Wiener Filter"]

        self.current_mode_index = 0  # Start with the first mode
        self.current_mode = self.modes[self.current_mode_index]  # Initialize current mode
        self.ui.toggle_mode_button.setText(self.current_mode)  # Set initial mode text on toggle button

        # Audio playback variables
        self.audio_segment = None
        self.playback_object = None

        # Frequency data variables
        self.freq_data = None
        self.freq_axis = None
        self.fs = None
        self.amplitude = None
        self.time = None

        # Sliders and frequency adjustment
        self.slidervalues = np.ones((10,), dtype=float)  # Default slider values for equalizer adjustments

        # Flags for initial plotting
        self.original_signal_plotted = False
        self.fourier_graph_initialized = False

        # Fourier magnitudes and display scale
        self.initial_fourier_magnitudes = None

        # Connect slider signals to callback functions
        for i, slider in enumerate(self.ui.equalizer_sliders):
            slider.sliderReleased.connect(self.create_slider_callback(i))

        # Initialize file and adjusted signal plot data
        self.current_file = None
        self.adjusted_signal_plot_data = None

        # Configure the default mode (Uniform Range Mode)
        self.configure_uniform_range_mode()

        self.ui.button.clicked.connect(self.noise_reduction)

    def setup_signals(self):
        # Connect template signals to respective functions
        self.ui.quit_app_button.clicked.connect(self.quit_app)
        # self.ui.toggle_mode_button.clicked.connect(self.apply_mode)
        self.ui.toggle_mode_button.clicked.connect(self.toggle_current_mode)
        self.ui.reset_button.clicked.connect(self.reset_signal)
        self.ui.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.ui.speed_button.clicked.connect(self.toggle_speed)
        self.ui.stop_button.clicked.connect(self.stop_signal)
        self.ui.toggle_spectrogram_button.clicked.connect(self.toggle_show_spectrogram)
        self.ui.toggle_scale_button.clicked.connect(self.toggle_scale_mode_2)

    def quit_app(self):
        QApplication.quit()
        remove_directories()

    def toggle_current_mode(self):
        # Increment the index and wrap around to the beginning if at the end
        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
        self.current_mode = self.modes[self.current_mode_index]  # Update current mode

        # Update the button text to the new mode
        self.ui.toggle_mode_button.setText(self.current_mode)
        self.apply_mode()
        self.reset_signal()

    def stop_signal(self):
        self.reset_signal()
        self.current_file = self.file_path  # Set the current file
        self.load_audio_signal(self.file_path)
        self.is_toggle = False
        self.update_audio_equalizer()

    def toggle_scale_mode_2(self):
        self.is_toggle = not self.is_toggle
        if self.current_mode == "Uniform Range":
            self.plot_signal_uniform(self.original_time, self.original_amplitude)
        if self.current_mode == "Hybrid Sounds" or self.current_mode == "Eliminates Vowels" or self.current_mode == "Wiener Filter":
            self.update_audio_equalizer()

    def apply_mode(self):
        mode_config = {
            "Hybrid Sounds": self.configure_hybrid_sounds_mode,
            "Eliminates Vowels": self.configure_vocals_mode,
            "Wiener Filter": self.configure_wiener_filter_mode,
            "Uniform Range": self.configure_uniform_range_mode,
        }
        mode_action = mode_config.get(self.current_mode)
        if mode_action:
            mode_action()
            self.setup_sliders()  # Update sliders based on the current mode

    def setup_sliders(self):
        # Reset sliders
        for slider in self.ui.equalizer_sliders:
            slider.blockSignals(True)  # Temporarily block signals
            slider.setValue(50)  # Reset to neutral position
            slider.blockSignals(False)  # Re-enable signals

        # Hide all sliders and labels
        for label, slider in zip(self.ui.equalizer_labels, self.ui.equalizer_sliders):
            label.setVisible(False)
            slider.setVisible(False)

        # Show sliders for the current mode
        num_sliders = len(self.labels)
        for i in range(num_sliders):
            self.ui.equalizer_labels[i].setText(self.labels[i])
            self.ui.equalizer_labels[i].setVisible(True)
            self.ui.equalizer_sliders[i].setVisible(True)

    def initialize_playback(self):
        # Initialize playback variables
        self.Timer_1 = QTimer()
        self.Timer_1.timeout.connect(self.update_cine)
        self.is_playing = False
        self.window_width = 1
        self.cine_index = 0
        self.original_time = []
        self.original_amplitude = []
        self.speeds = [1, 2, 4, 16, 32, 0.5]
        self.current_speed_index = 0
        self.current_speed = self.speeds[self.current_speed_index]

        # Store the audio data for playback
        self.audio_data = None
        self.sampling_rate = None
        self.playback_index = 0
        self.playback_speed_factor = 1
        # Timer for playback
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_playback)

    def configure_uniform_range_mode(self):
        self.labels = ["Slider 1", "Slider 2", "Slider 3", "Slider 4", "Slider 5", "Slider 6", "Slider 7", "Slider 8",
                       "Slider 9", "Slider 10"]
        self.ui.button.hide()
        self.ui.upload_signal_button.disconnect()
        self.ui.upload_signal_button.clicked.connect(self.upload_signal_file)
        self.load_signal_data(
            "static/data/rectangular/generated_signal_10.0Hz_60.0Hz_110.0Hz_160.0Hz_210.0Hz_260.0Hz_310.0Hz_360.0Hz_410.0Hz_460.0Hz.csv"
        )

    def configure_hybrid_sounds_mode(self):
        self.labels = ["Wolf", "Owl", "Birds", "Studio", "80s sine synth"]
        self.frequency_ranges = [
            (0, 600),
            (600, 800),
            (1800, 5500),
            (1200, 1800),
            (5500, 20000),
        ]
        self.configure_sliders()

    def configure_vocals_mode(self):
        self.labels = ["Keyboard", "synth", "C", "A "]
        self.frequency_ranges = [
        (0, 50),  # A
        (6000, 7000),  # A
        (2000, 5000),  # C
        (600, 800),  # C+A
        ]
        self.configure_sliders()

    def configure_sliders(self):
        # Configure sliders for sounds
        for slider in self.ui.equalizer_sliders[:4]:
            slider.setMinimum(0)  # Minimum gain (mute)
            slider.setMaximum(100)  # Maximum gain (boost)
            slider.setValue(50)  # Default gain (no change)
            slider.sliderReleased.connect(self.update_audio_equalizer)

        self.ui.upload_signal_button.disconnect()
        self.ui.upload_signal_button.clicked.connect(self.upload_audio_signal_file)

    def upload_signal_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signal File",
            "static/data/rectangular/",
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        # If a file is selected, set current_file and load it
        if file_path:
            self.current_file = file_path  # Set the current file
            self.load_signal_data(file_path)

    def toggle_speed(self):
        """Cycle through the available speeds and apply the new speed immediately during playback."""
        # Cycle through the available speeds
        self.current_speed_index = (self.current_speed_index + 1) % len(self.speeds)
        self.current_speed = self.speeds[self.current_speed_index]

        # Update the button text to reflect the new speed setting
        if isinstance(self.current_speed, int):
            speed_text = f"{self.current_speed}X"
        else:
            speed_text = f"{self.current_speed:.1f}X"
        self.ui.speed_button.setText(speed_text)

        # Adjust the playback speed both for audio and visualization
        self.update_playback_interval()  # Update graph interval
        self.adjust_audio_speed()  # Adjust audio playback speed

    def adjust_audio_speed(self):
        """Adjust the playback speed of the audio."""
        if self.audio_data is None:
            return

        # Adjust the audio playback speed by modifying the samplerate
        adjusted_samplerate = int(self.sampling_rate * self.current_speed)

        if hasattr(self, 'audio_stream') and self.audio_stream.active:
            self.audio_stream.stop()
            self.audio_stream.close()

        # Create a new audio stream with the adjusted sampling rate
        self.audio_stream = sd.OutputStream(
            samplerate=adjusted_samplerate,
            channels=1,
            callback=self.audio_callback
        )

        # Restart the audio stream
        self.audio_stream.start()

    def update_playback_interval(self):
        """Set the playback timer interval based on the current speed."""
        base_interval = 50  # Base interval in milliseconds for 1x speed
        adjusted_interval = int(base_interval / self.current_speed) if self.current_speed != 0 else base_interval

        # Update the Timer interval to control the speed of the graph
        self.Timer_1.setInterval(adjusted_interval)

    def toggle_play_pause(self):
        if self.current_file is None:
            QMessageBox.warning(self, "No File Loaded", "Please load a file before playing.")
            return

        file_extension = self.current_file.split('.')[-1]

        if self.ui.play_pause_button.text() == "Play":
            self.ui.play_pause_button.setText("Pause")

            # Start or resume playback based on file type
            if file_extension == "wav":
                if not self.is_playing:  # Start playback only if not already playing
                    self.play_audio()
                    self.play_timer.start(30)  # Update every 30 ms
            elif file_extension == "csv":
                self.Timer_1.start(50)

            self.is_playing = True

        else:
            self.ui.play_pause_button.setText("Play")
            self.is_playing = False

            # Save the current audio position for resuming
            if file_extension == "wav":
                if hasattr(self, "audio_stream") and self.audio_stream.active:
                    self.audio_stream.stop()
                if hasattr(self, "play_timer"):
                    self.play_timer.stop()
            self.Timer_1.stop()

    def play_audio(self):
        if self.audio_data is None:
            return

        # Adjust the playback sampling rate for slower playback
        adjusted_sampling_rate = int(self.sampling_rate * self.playback_speed_factor)

        # Create a Stream for audio playback
        self.audio_stream = sd.OutputStream(
            samplerate=adjusted_sampling_rate,  # Use the adjusted sampling rate
            channels=1,
            callback=self.audio_callback
        )

        # Start playback
        self.audio_stream.start()

    def update_playback(self):
        if self.audio_data is None or len(self.audio_data) == 0:
            return

        # Calculate the playback chunk based on the current speed
        chunk_size = int(0.003 * self.sampling_rate * self.current_speed)  # Adjust chunk size for speed
        start_index = self.playback_index
        end_index = start_index + chunk_size

        if start_index >= len(self.audio_data):
            # Stop playback when the audio ends
            self.stop_audio()
            return

        # Handle partial data at the end of the file
        if end_index > len(self.audio_data):
            end_index = len(self.audio_data)

        # Update the graph with the current playback chunk
        self.input_cine_graph.clear()
        self.input_cine_graph.enableAutoRange(axis='x')
        self.output_cine_graph.clear()
        self.output_cine_graph.enableAutoRange(axis='x')

        time_axis = np.linspace(0, len(self.audio_data) / self.sampling_rate, len(self.audio_data))
        self.input_cine_graph.plot(
            time_axis[start_index:end_index], self.audio_data[start_index:end_index], pen='b'
        )
        self.output_cine_graph.plot(
            time_axis[start_index:end_index], self.audio_data[start_index:end_index], pen='r'
        )

        # Increment playback_index
        self.playback_index += chunk_size

    def audio_callback(self, outdata, frames, time, status):
        if self.audio_data is None or self.frequency_ranges is None or self.audio_stream is None:
            outdata[:] = np.zeros((frames, 1))  # Fill with silence if no data
            return

        # Extract the current chunk of audio data
        start_index = self.playback_index
        end_index = start_index + frames

        if start_index >= len(self.audio_data):
            outdata[:] = np.zeros((frames, 1))
            self.stop_audio()
            return

        if end_index > len(self.audio_data):
            chunk = self.audio_data[start_index:]
            outdata[:len(chunk)] = chunk.reshape(-1, 1)
            outdata[len(chunk):] = 0
            self.playback_index = len(self.audio_data)
            self.stop_audio()
            return

        # Normal case: Process a full chunk
        chunk = self.audio_data[start_index:end_index]

        # Apply frequency adjustments (equalizer)
        fft_data = np.fft.rfft(chunk)  # Perform Fourier Transform
        fft_freqs = np.fft.rfftfreq(len(chunk), d=1 / self.sampling_rate)

        # Get the value of the first slider
        first_slider_gain = self.ui.equalizer_sliders[0].value() / 50.0  # Normalize gain

        # Apply gain to the first frequency range (0-600) and (800-1200)
        freq_mask_1 = (fft_freqs >= 0) & (fft_freqs <= 600)
        freq_mask_2 = (fft_freqs >= 800) & (fft_freqs <= 1200)
        fft_data[freq_mask_1] *= first_slider_gain  # Apply gain to 0-600 Hz
        fft_data[freq_mask_2] *= first_slider_gain  # Apply gain to 800-1200 Hz



        # Perform Inverse Fourier Transform to get the modified audio
        adjusted_chunk = self.call_inverese_fourier(fft_data,fft_freqs)#.astype(np.float32)

        # Fill the output buffer with the modified chunk
        outdata[:len(adjusted_chunk)] = adjusted_chunk.reshape(-1, 1)
        outdata[len(adjusted_chunk):] = 0  # Fill remaining frames with silence

        # Increment playback index
        self.playback_index += frames

    def stop_audio(self):
        if hasattr(self, "audio_stream") and self.audio_stream is not None:
            if self.audio_stream.active:
                self.audio_stream.stop()
            self.audio_stream = None
        if hasattr(self, "play_timer"):
            self.play_timer.stop()

        self.is_playing = False
        self.ui.play_pause_button.setText("Play")
        self.playback_index = 0

    def update_audio_equalizer(self):
        if self.audio_data is None or self.frequency_ranges is None:
            return

        # Perform Fourier Transform on the audio data
        fft_data = np.fft.rfft(self.audio_data)
        fft_freqs = np.fft.rfftfreq(len(self.audio_data), d=1 / self.sampling_rate)

        # if self.ui.input_spectrogram_container.isVisible():
        if not self.ui.input_spectrogram_container.isVisible():
            pass

        self.plot_spectrogram(self.audio_data, is_audio=True, output=False)

        # Get positive frequencies and corresponding magnitude
        positive_freqs = fft_freqs[:len(fft_freqs) // 2]
        positive_magnitudes = np.abs(fft_data[:len(fft_data) // 2])

        self.fourier_graph.clear()
        if self.is_toggle:
            freq_axis = self.freq_axis[:len(self.freq_axis)]
            # Calculate the dB scale if toggle is enabled
            freq_data_magnitude_db = 20 * np.log10(positive_magnitudes + 1e-10)  # Avoid log(0)

            # Call the audiogram plotting function
            audiogram_data = {
                "Left": {freq: mag for freq, mag in zip(freq_axis, freq_data_magnitude_db) if freq <= 500},
                # Example range
                "Right": {freq: mag for freq, mag in zip(freq_axis, freq_data_magnitude_db) if freq > 500}
                # Example range
            }
            self.plot_audiogram(audiogram_data)
        else:
            self.fourier_graph.plot(positive_freqs, positive_magnitudes, pen='r')  # Plot FFT results
            # Plot the Fourier data
            self.fourier_graph.setLabel('left', 'Amplitude')
            self.fourier_graph.setLabel('bottom', 'Frequency (Hz)')

        # Perform Inverse Fourier Transform to get the adjusted audio
        self.adjusted_audio_data = self.call_inverese_fourier(fft_data , fft_freqs)

        # Plot the spectrogram (output audio)
        if not self.ui.input_spectrogram_container.isVisible():
            pass
        self.plot_spectrogram(self.adjusted_audio_data, is_audio=True, output=True)

        # Update the output cine graph
        time_axis = np.linspace(0, len(self.adjusted_audio_data) / self.sampling_rate, len(self.adjusted_audio_data))
        self.output_cine_graph.clear()
        self.output_cine_graph.plot(time_axis, self.adjusted_audio_data, pen='r')

    def init_graph_widgets(self):
        # Cine Signal Viewers with zoom-enabled ViewBox
        self.input_cine_graph = PlotWidget(self.ui.input_cine_container)
        self.input_cine_graph.setGeometry(QRect(5, 25, 535, 165))
        self.input_cine_graph.setBackground('w')
        self.input_cine_graph.showGrid(x=True, y=True)
        self.input_cine_graph.setMouseEnabled(x=True, y=True)

        # Cine Signal Viewers with zoom-enabled ViewBox
        self.output_cine_graph = PlotWidget(self.ui.output_cine_container)
        self.output_cine_graph.setGeometry(QRect(5, 25, 1100, 165))
        self.output_cine_graph.setBackground('w')
        self.output_cine_graph.showGrid(x=True, y=True)
        self.output_cine_graph.setMouseEnabled(x=True, y=True)

        # Fourier Transform Graph (no zooming or panning)
        self.fourier_graph = PlotWidget(self.ui.frequency_domain_container)
        self.fourier_graph.setGeometry(QRect(5, 25, 535, 165))
        self.fourier_graph.setBackground('w')
        self.fourier_graph.showGrid(x=True, y=True)
        self.fourier_graph.setMouseEnabled(x=True, y=True)  # Disable zooming and panning for Fourier graph

        # Create a Matplotlib figure and embed it in the PyQt5 widget
        self.input_spectrogram_graph = FigureCanvas(plt.Figure(figsize=(2.5, 2)))  # Create a figure with desired size
        self.ui.input_spectrogram_container.layout().addWidget(self.input_spectrogram_graph)

        # Output Spectrogram Graph (no zooming or panning)
        self.output_spectrogram_graph = FigureCanvas(plt.Figure(figsize=(2.5, 2)))  # Create a figure with desired size
        self.ui.output_spectrogram_container.layout().addWidget(self.output_spectrogram_graph)

    def load_signal_data(self, file_path):
        try:
            # Load data from CSV, excluding the first row (headers)
            data = np.loadtxt(file_path, delimiter=',', skiprows=1)
            self.current_file = file_path

            # Assuming the first column is time and the second is amplitude
            self.original_time = data[:, 0]
            self.original_amplitude = data[:, 1]

            # Set self.amplitude and self.fs
            self.amplitude = self.original_amplitude
            self.time = self.original_time
            self.fs = 1000  # Update this if your sampling rate changes

            # Reset the original signal plotted flag
            self.original_signal_plotted = False

            # Reset Fourier graph flag when loading a new signal
            self.fourier_graph_initialized = False

            # Reset sliders to default values
            self.reset_sliders()

            # Plot the signal data
            if self.current_mode == "Uniform Range":
                self.plot_signal_uniform(self.original_time, self.original_amplitude)
            elif self.current_mode == "Wiener Filter":
                self.plot_wiener_graphs(self.original_time, self.original_amplitude)

            # Update the status bar to show file loaded status
            self.freq_data = rfft(self.amplitude)
            self.freq_axis = rfftfreq(len(self.amplitude), 1 / self.fs)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load the file:\n{str(e)}")

    def upload_audio_signal_file(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "static/data/WAV/",
            "Audio Files (*.wav *.mp3);;All Files (*)",
            options=options
        )

        # If a file is selected, set current_file and load it
        if self.file_path:
            self.reset_signal()
            self.current_file = self.file_path  # Set the current file
            self.load_audio_signal(self.file_path)
            self.is_toggle = False
            self.update_audio_equalizer()

    def load_audio_signal(self, file_path):
        """Load audio signal from a file, plot it, and calculate its frequency data."""
        try:
            # Load audio data
            self.audio_data, self.sampling_rate = librosa.load(file_path, sr=None)

            # Plot the audio signal in the input_cine_graph
            time_axis = np.linspace(0, len(self.audio_data) / self.sampling_rate, len(self.audio_data))
            self.input_cine_graph.clear()
            self.input_cine_graph.plot(time_axis, self.audio_data, pen='b')  # Plot actual data instead of zeros
            self.output_cine_graph.clear()
            self.output_cine_graph.plot(time_axis, self.audio_data, pen='r')  # Plot actual data instead of zeros

            # FFT computation
            fft_result = np.fft.fft(self.audio_data)
            freq_axis = np.fft.fftfreq(len(self.audio_data), d=1 / self.sampling_rate)

            # Get positive frequencies and corresponding magnitude
            positive_freqs = freq_axis[:len(freq_axis) // 2]
            positive_magnitudes = np.abs(fft_result[:len(fft_result) // 2])

            # Normalize or cap the magnitudes to a reasonable level
            max_allowed_magnitude = 100  # Example cap value
            positive_magnitudes = np.clip(positive_magnitudes, 0, max_allowed_magnitude)

            # Plot frequency data on fourier_graph
            self.fourier_graph.clear()
            self.fourier_graph.plot(positive_freqs, positive_magnitudes, pen='r')  # Plot FFT results

            # ---- Reset playback parameters ----
            self.playback_index = 0
            self.is_playing = False
            self.ui.play_pause_button.setText("Play")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audio file:\n{str(e)}")

    def update_cine(self):
        # Only proceed if we are within the range of the data
        if self.cine_index < len(self.original_time):
            # Plot data incrementally for a smooth animation effect
            self.input_cine_graph.plot(self.original_time[:self.cine_index],
                                       self.original_amplitude[:self.cine_index],
                                       pen=pg.mkPen('b', width=2), clear=True)

            # Increment the index to move forward in the animation
            self.cine_index += 1
        else:
            # Stop playback at the end of the data
            self.Timer_1.stop()
            self.is_playing = False
            self.ui.play_pause_button.setText("Play")
            self.cine_index = 0

    def reset_signal(self):
        # Clear both graphs
        self.input_cine_graph.clear()
        self.fourier_graph.clear()
        self.output_cine_graph.clear()
        self.setup_spectrogram()

        # Reset playback variables
        self.current_file = None
        self.cine_index = 0
        self.is_playing = False
        self.audio_data = None
        self.sampling_rate = None
        self.playback_index = 0
        self.playback_speed_factor = 1

        # Set x and y ranges to default
        self.input_cine_graph.setXRange(0, self.window_width)
        self.output_cine_graph.setXRange(0, self.window_width)
        self.fourier_graph.setXRange(0, self.window_width)  # Adjust based on your preferred default range

        # Update button text if playback was active
        self.ui.play_pause_button.setText("Play")
        self.Timer_1.stop()
        self.stop_audio()

        # Redraw the plot widget
        self.input_cine_graph.plotItem.getViewBox().update()
        self.output_cine_graph.plotItem.getViewBox().update()
        self.fourier_graph.plotItem.getViewBox().update()

    def setup_spectrogram(self):
        # Clear the matplotlib spectrogram graph
        if hasattr(self.input_spectrogram_graph, "figure"):
            self.input_spectrogram_graph.figure.clear()
            ax1 = self.input_spectrogram_graph.figure.add_subplot(111)
            ax1.set_title("Signal Spectrogram Input")
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Frequency (Hz)")
            self.input_spectrogram_graph.draw()
        if hasattr(self.output_spectrogram_graph, "figure"):
            self.output_spectrogram_graph.figure.clear()
            ax2 = self.output_spectrogram_graph.figure.add_subplot(111)
            ax2.set_title("Signal Spectrogram Output")
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Frequency (Hz)")
            # self.output_spectrogram_graph.figure.tight_layout()  # Ensure labels fit well
            self.output_spectrogram_graph.draw()

    def create_slider_callback(self, slider_index):
        """Create a callback function for each slider to update the plot based on its value."""

        def callback():
            # Ensure valid data is loaded before adjusting
            if self.original_time is not None and self.original_amplitude is not None:
                # Update the slider value for the correct index
                slider_value = self.ui.equalizer_sliders[slider_index].value() / 50  # Normalize around 1

                # Apply the slider effect with a smooth influence across all frequency bands
                for i in range(len(self.slidervalues)):
                    # Apply a scaled influence based on the distance from the adjusted slider
                    distance_factor = np.exp(-abs(i - slider_index))  # Exponential decay for smooth transitions
                    self.slidervalues[i] = slider_value * distance_factor + self.slidervalues[i] * (1 - distance_factor)

                if self.current_mode == "Uniform Range":
                    # Plot the signal with the updated slidervalues to see effects across the entire frequency domain
                    self.plot_signal_uniform(self.original_time, self.original_amplitude, fs=self.fs)
                elif self.current_mode == "Wiener Filter":
                    self.plot_wiener_graphs(self.original_time, self.original_amplitude)
                elif self.current_mode == "Musical Instrument" or self.current_mode == "Eliminates Vowels":
                    self.update_audio_equalizer()

        return callback

    def plot_signal_uniform(self, time, amplitude, fs=1000, threshold_factor=0.05):
        # Plot the original signal only once
        if not hasattr(self, "original_signal_plotted") or not self.original_signal_plotted:
            self.input_cine_graph.clear()
            self.output_cine_graph.clear()

            # Plot the original signal in blue for time vs amplitude on input_cine_graph
            self.input_cine_graph.plot(time, amplitude, pen=pg.mkPen(color="#800080", width=2))
            self.input_cine_graph.plotItem.setLabel('bottom', 'Time')
            self.input_cine_graph.plotItem.setLabel('left', 'Amplitude')
            self.original_signal_plotted = True  # Prevent re-plotting of original signal

        # Store the original signal data for playback and further operations
        self.original_time = time
        self.original_amplitude = amplitude
        if not self.ui.input_spectrogram_container.isVisible():
            pass
        self.plot_spectrogram((time, amplitude), is_audio=False, output=False)

        # Calculate the Fourier Transform of the original signal
        N = len(amplitude)
        freq_data = rfft(amplitude)  # Real FFT for positive frequencies
        frequencies = rfftfreq(N, 1 / fs)  # Frequency axis in Hz
        magnitude = np.abs(freq_data)

        # Set initial y-axis range with a buffer to avoid clipping
        if not hasattr(self, "initial_y_range"):
            max_magnitude = max(magnitude)
            self.initial_y_range = (0, max_magnitude)  # Add 10% buffer to max magnitude

        # Save initial Fourier magnitudes if needed for restoration
        if not hasattr(self, "initial_fourier_magnitudes"):
            self.initial_fourier_magnitudes = magnitude.copy()

        # Define 10 custom frequency ranges
        self.frequency_ranges = [
            (0, 50),
            (50, 100),
            (100, 150),
            (150, 200),
            (200, 250),
            (250, 300),
            (300, 350),
            (350, 400),
            (400, 450),
            (450, 500)
        ]

        # Clone the original frequency data to apply selective adjustments
        adjusted_freq_data = freq_data.copy()

        # Inverse Fourier Transform to get the adjusted signal back in the time domain
        adjusted_signal = self.call_inverese_fourier(adjusted_freq_data , frequencies)
        self.adjusted_signal_plot_data = adjusted_signal  # Set this to avoid AttributeError
        if not self.ui.input_spectrogram_container.isVisible():
            pass
        self.plot_spectrogram((time, adjusted_signal), is_audio=False, output=True)

        # Plot the adjusted signal on output_cine_graph
        self.output_cine_graph.clear()
        self.output_cine_graph.plot(time, adjusted_signal, pen=pg.mkPen(color="b", width=2))
        self.output_cine_graph.plotItem.setLabel('bottom', 'Time')
        self.output_cine_graph.plotItem.setLabel('left', 'Amplitude')

        # Set the Fourier Transform plot range based on the highest significant frequency
        max_significant_freq = frequencies[
            np.max(np.where(np.abs(adjusted_freq_data) > threshold_factor * max(np.abs(adjusted_freq_data))))]

        # Update the Fourier Transform plot with adjusted amplitudes
        self.fourier_graph.clear()
        if self.is_toggle:
            freq = [10.0, 60.0, 110.0, 160.0, 210.0, 260.0, 310.0, 360.0, 410.0, 460.0]
            freq_data_magnitude_db = []
            freq_data_magnitude_db_2 = []
            # Calculate the dB scale if toggle is enabled
            for mag in magnitude:
                if mag > 0:
                    freq_data_magnitude_db.append(20 * np.log10(mag))  # Avoid log(0)
            for ind, mag in enumerate(freq_data_magnitude_db):
                if mag < 0:
                    freq_data_magnitude_db_2.append(mag)

            # Call the audiogram plotting function
            audiogram_data = {
                "Left": {fr: mag for fr, mag in zip(freq, freq_data_magnitude_db_2) if fr <= 500},
                # Example range
                "Right": {fr: mag for fr, mag in zip(freq, freq_data_magnitude_db_2) if fr > 500}
                # Example range
            }
            self.plot_audiogram(audiogram_data)
        else:
            self.fourier_graph.plot(frequencies, np.abs(adjusted_freq_data), pen='r')
            self.fourier_graph.setLogMode(y=False)
            # Plot the Fourier data
            self.fourier_graph.setLabel('left', 'Amplitude')
            self.fourier_graph.setLabel('bottom', 'Frequency (Hz)')

        # Disable auto-range for y-axis to lock the scaling
        self.fourier_graph.plotItem.vb.disableAutoRange(axis=pg.ViewBox.YAxis)

        # Save adjusted signal data for further reference
        self.adjusted_signal_plot_data = adjusted_signal

    def reset_sliders(self):
        """Reset all sliders to their default middle position."""
        for slider in self.ui.equalizer_sliders:
            slider.setValue(100)  # Set to middle value, assuming range is 0-100

    def define_frequency_bands(self, fs, num_sliders=10):
        """Define frequency bands for each slider."""
        max_freq = fs / 2
        band_width = max_freq / num_sliders
        frequency_bands = [(i * band_width, (i + 1) * band_width) for i in range(num_sliders)]
        return frequency_bands

    def call_inverese_fourier(self, data ,fft_freqs):
        # Apply gain to other frequency ranges
        for slider, freq_range in zip(self.ui.equalizer_sliders[1:], self.frequency_ranges[1:]):
            gain = slider.value() / 50.0  # Normalize gain
            freq_mask = (fft_freqs >= freq_range[0]) & (fft_freqs <= freq_range[1])
            data[freq_mask] *= gain  # Apply gain to the selected frequency range

        return np.fft.irfft(data)

    def plot_spectrogram(self, input_data, is_audio=False, output=False):
        """
        Plots the spectrogram for the given audio or signal data.
        Parameters:
            input_data: Raw signal data (e.g., np.array for audio) or tuple (time, amplitude)
            is_audio: Set to True for audio data; otherwise, False.
            output: Set to True to plot on the output spectrogram graph; otherwise, input graph.
        """
        # Determine the target graph (input or output spectrogram)
        target_graph = self.output_spectrogram_graph if output else self.input_spectrogram_graph

        # Clear the previous spectrogram plot
        target_graph.figure.clear()
        ax = target_graph.figure.add_subplot(111)

        if is_audio:
            # Process raw audio data (input_data is assumed to be a NumPy array here)
            signal = input_data
            sample_rate = self.sampling_rate

            # Compute Short-Time Fourier Transform (STFT)
            stft = librosa.stft(signal, n_fft=2048, hop_length=512)
            spectro = np.abs(stft)
            spectrogram_db = librosa.amplitude_to_db(spectro, ref=np.max)

            # Plot the spectrogram in decibels (dB)
            img = librosa.display.specshow(
                spectrogram_db,
                y_axis='log',
                x_axis='time',
                sr=sample_rate,
                hop_length=512,
                cmap='inferno',
                ax=ax
            )
            ax.set_title('Spectrogram' + (' (Output)' if output else ' (Input)'))
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Frequency (Hz)')

            # Add a colorbar
            target_graph.figure.colorbar(img, ax=ax, format='%+2.0f dB')

        else:
            # Assuming input_data is a tuple with (time, amplitude)
            time, amplitude = input_data
            fs = self.fs  # Sampling frequency

            # Compute the spectrogram
            f, t, Sxx = spectrogram(amplitude, fs=fs)

            # Plot the spectrogram in dB
            cax = ax.pcolormesh(t, f, 10 * np.log10(np.maximum(Sxx, 1e-10)), shading='auto')
            ax.set_title('Signal Spectrogram' + (' (Output)' if output else ' (Input)'))
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Frequency (Hz)')

            # Add a colorbar
            target_graph.figure.colorbar(cax, ax=ax, label='Power [dB]')

        # Redraw the canvas to update the graph
        target_graph.draw()

    def toggle_show_spectrogram(self):
        spectrogram_visible = self.ui.input_spectrogram_container.isVisible()

        # Toggle visibility of spectrogram containers
        self.ui.input_spectrogram_container.setVisible(not spectrogram_visible)
        self.ui.output_spectrogram_container.setVisible(not spectrogram_visible)

        # Update button text based on visibility
        self.ui.toggle_spectrogram_button.setText("Hide Spectrogram" if not spectrogram_visible else "Show Spectrogram")

        if spectrogram_visible:
            # Arrange containers vertically without spectrograms
            self.ui.graphs_container.addWidget(self.ui.input_cine_container, 0, 0, 0, 2)
            self.ui.graphs_container.addWidget(self.ui.output_cine_container, 1, 0, 1, 2)
            self.ui.graphs_container.addWidget(self.ui.playback_controls, 2, 0, 1, 2)
            self.ui.graphs_container.addWidget(self.ui.frequency_domain_container, 3, 0, 1, 2)

            self.input_cine_graph.setGeometry(QRect(5, 25, 1100, 180))
            self.output_cine_graph.setGeometry(QRect(5, 25, 1100, 180))
            self.fourier_graph.setGeometry(QRect(5, 25, 1100, 180))

        else:
            # Restore original grid layout with spectrograms
            self.ui.graphs_container.addWidget(self.ui.input_cine_container, 0, 0)
            self.ui.graphs_container.addWidget(self.ui.frequency_domain_container, 0, 1)
            self.ui.graphs_container.addWidget(self.ui.output_cine_container, 1, 0, 1, 2)
            self.ui.graphs_container.addWidget(self.ui.playback_controls, 2, 0, 1, 2)
            self.ui.graphs_container.addWidget(self.ui.input_spectrogram_container, 3, 0)
            self.ui.graphs_container.addWidget(self.ui.output_spectrogram_container, 3, 1)

            self.input_cine_graph.setGeometry(QRect(5, 25, 535, 165))
            self.fourier_graph.setGeometry(QRect(5, 25, 535, 165))
            self.output_cine_graph.setGeometry(QRect(5, 25, 1100, 165))
            self.input_spectrogram_graph.setGeometry(QRect(5, 25, 535, 165))
            self.output_spectrogram_graph.setGeometry(QRect(5, 25, 535, 165))

        # Update the layout immediately to reflect changes
        self.ui.graphs_container.update()
        self.ui.graphs_container.parentWidget().update()

    # --------------------------------------------------------------------------------------------------------------------------------------

    def configure_wiener_filter_mode(self):
        self.ui.button.setVisible(True)
        self.labels = []

    def noise_reduction(self):
        # If a file is selected, set current_file and load it
        if self.current_file:
            # Apply Wiener filtering if the file is a WAV file
            if self.current_file.endswith('.wav'):
                noise_begin, noise_end = 0, 1
                wiener_filter = nr.Wiener(self.current_file, noise_begin, noise_end)  # Adjust noise time as needed

                wiener_filter.wiener()  # Apply Wiener filtering
                # Load the filtered audio for playback
                self.audio_data, self.sampling_rate = librosa.load('static/data/WAV/Filtered Guitar.wav', sr=None)
                self.update_audio_equalizer()  # Update the equalizer with the new audio

    def plot_audiogram(self, audiogram, plot_widget=None, classification=False):
        if plot_widget is None:
            plot_widget = self.fourier_graph

        if classification:
            self.plot_classification(plot_widget)

        if isinstance(audiogram, dict):
            plot_widget.plot(x=list(audiogram['Left'].keys()), y=list(audiogram['Left'].values()),
                             pen=mkPen('b', width=2),
                             symbol='x', name='Left')
            plot_widget.plot(x=list(audiogram['Right'].keys()), y=list(audiogram['Right'].values()),
                             pen=mkPen('r', width=2), symbol='o', symbolBrush='w', name='Right')

        plot_widget.plotItem.setLabel('bottom', 'Frequency (Hz)')
        plot_widget.plotItem.setLabel('left', 'dB')

        plot_widget.enableAutoRange('xy', False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainApp()
    mainWindow.showFullScreen()
    sys.exit(app.exec_())
