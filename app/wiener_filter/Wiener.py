import numpy as np
from scipy.fftpack import fft, ifft
import scipy.io.wavfile as wav


class Wiener:
    """
    Class made for wiener filtering based on the article "Improved Signal-to-Noise Ratio Estimation for Speech
    Enhancement".

    Reference :
        Cyril Plapous, Claude Marro, Pascal Scalart. Improved Signal-to-Noise Ratio Estimation for Speech
        Enhancement. IEEE Transactions on Audio, Speech and Language Processing, Institute of Electrical
        and Electronics Engineers, 2006.

    """

    def __init__(self, WAV_FILE, *T_NOISE):
        """
        Input :
            WAV_FILE
            T_NOISE : float, Time in seconds /!\ Only works if stationnary noise is at the beginning of x /!\

        """
        # Constants are defined here
        self.WAV_FILE, self.T_NOISE = WAV_FILE, T_NOISE
        self.FS, self.x = wav.read(self.WAV_FILE)
        self.NFFT, self.SHIFT, self.T_NOISE = 2 ** 10, 0.5, T_NOISE
        self.FRAME = int(0.02 * self.FS)  # Frame of 20 ms

        # Computes the offset and number of frames for overlapp - add method.
        self.OFFSET = int(self.SHIFT * self.FRAME)

        # Hanning window and its energy Ew
        def hann_window(N):
            return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N) / (N - 1))

        self.WINDOW = hann_window(self.FRAME)
        self.EW = np.sum(self.WINDOW)

        self.channels = np.arange(self.x.shape[1]) if self.x.shape != (self.x.size,) else np.arange(1)
        length = self.x.shape[0] if len(self.channels) > 1 else self.x.size
        self.frames = np.arange((length - self.FRAME) // self.OFFSET + 1)
        # Evaluating noise psd with n_noise
        self.Sbb = self.welchs_periodogram()

    @staticmethod
    def a_posteriori_gain(SNR):
        """
        Function that computes the a posteriori gain G of Wiener filtering.

            Input :
                SNR : 1D np.array, Signal to Noise Ratio
            Output :
                G : 1D np.array, gain G of Wiener filtering

        """
        G = (SNR - 1) / SNR
        return G

    @staticmethod
    def a_priori_gain(SNR):
        """
        Function that computes the a priori gain G of Wiener filtering.

            Input :
                SNR : 1D np.array, Signal to Noise Ratio
            Output :
                G : 1D np.array, gain G of Wiener filtering

        """
        G = SNR / (SNR + 1)
        return G

    def welchs_periodogram(self):
        """
        Estimation of the Power Spectral Density (Sbb) of the stationnary noise
        with Welch's periodogram given prior knowledge of n_noise points where
        speech is absent.

            Output :
                Sbb : 1D np.array, Power Spectral Density of stationnary noise

        """
        # Initialising Sbb
        Sbb = np.zeros((self.NFFT, self.channels.size))

        self.N_NOISE = int(self.T_NOISE[0] * self.FS), int(self.T_NOISE[1] * self.FS)
        # Number of frames used for the noise
        noise_frames = np.arange(((self.N_NOISE[1] - self.N_NOISE[0]) - self.FRAME) // self.OFFSET + 1)
        for channel in self.channels:
            for frame in noise_frames:
                i_min, i_max = frame * self.OFFSET + self.N_NOISE[0], frame * self.OFFSET + self.FRAME + self.N_NOISE[0]
                x_framed = self.x[i_min:i_max, channel] * self.WINDOW
                X_framed = fft(x_framed, self.NFFT)
                Sbb[:, channel] = frame * Sbb[:, channel] / (frame + 1) + np.abs(X_framed) ** 2 / (frame + 1)
        return Sbb

    def moving_average(self):
        # Initialising Sbb
        Sbb = np.zeros((self.NFFT, self.channels.size))
        # Number of frames used for the noise
        noise_frames = np.arange((self.N_NOISE - self.FRAME) + 1)
        for channel in self.channels:
            for frame in noise_frames:
                x_framed = self.x[frame:frame + self.FRAME, channel] * self.WINDOW
                X_framed = fft(x_framed, self.NFFT)
                Sbb[:, channel] += np.abs(X_framed) ** 2
        return Sbb / noise_frames.size

    def wiener(self):
        """
        Function that returns the estimated speech signal using overlapp - add method
        by applying a Wiener Filter on each frame to the noised input signal.

            Output :
                s_est : 1D np.array, Estimated speech signal

        """
        # Initialising estimated signal s_est
        s_est = np.zeros(self.x.shape)
        for channel in self.channels:
            for frame in self.frames:
                ############# Initialising Frame ###################################
                # Temporal framing with a Hanning window
                i_min, i_max = frame * self.OFFSET, frame * self.OFFSET + self.FRAME
                x_framed = self.x[i_min:i_max, channel] * self.WINDOW

                # Zero padding x_framed
                X_framed = fft(x_framed, self.NFFT)

                ############# Wiener Filter ########################################
                # Apply a priori wiener gains G to X_framed to get output S
                SNR_post = (np.abs(X_framed) ** 2 / self.EW) / self.Sbb[:, channel]
                G = Wiener.a_priori_gain(SNR_post)
                S = X_framed * G

                ############# Temporal estimated Signal ############################
                # Estimated signals at each frame normalized by the shift value
                temp_s_est = np.real(ifft(S)) * self.SHIFT
                s_est[i_min:i_max, channel] += temp_s_est[:self.FRAME]  # Truncating zero padding
        wav.write('static/data/WAV/Filtered Guitar.wav', self.FS, s_est / s_est.max())
