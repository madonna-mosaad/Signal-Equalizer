def dictify(self, r, root=True):
    '''
    Create dictionary from root XML object.
    Input:
        r: root from xml.etree.ElementTree. This is done
           by the parse_audiometry function
    Output:
        d [dict] : dictionary of all the data in the xml file.
    Thanks to Erik Aronesty - see StackOverflow post
    https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary
    '''
    if root:
        return {re.sub('{.*}', '', r.tag): self.dictify(r, False)}
    d = copy(r.attrib)
    if r.text:
        d["_text"] = r.text
    for x in r.findall("./*"):
        x.tag = re.sub('{.*}', '', x.tag)
        if x.tag not in d:
            d[x.tag] = []
        d[x.tag].append(self.dictify(x, False))
    return d


def parse_audiometry(self, xml_file):
    '''
    Parse audiometry XML file. This takes the Otoaccess XML files that have
    been exported and parses out the relevant pure tone data.

    Input:
        xml_file [str] : Path to your XML file for loading.

    Output:
        audiogram [dict] : Dictionary containing audiogram data.
    '''
    tree = ET.parse(xml_file)
    r = tree.getroot()

    audiogram = {
        "Left": {},
        "Right": {}
    }

    # Extract data from XML
    for row in r.findall('row'):
        time_value = float(row.find('Time').text)
        signal_value = float(row.find('Signal').text)

        # Assuming that the signal values are for both left and right ears
        # You may need to adjust the logic here based on how your data is structured
        if signal_value < 0:  # Example condition for left ear
            audiogram["Left"][time_value] = signal_value
        else:  # Example condition for right ear
            audiogram["Right"][time_value] = signal_value

    return audiogram


def plot_classification(self, plot_widget, fontsize='small'):
    levels = {
        'Normal': [-10, 15, '#9d9bc1'],
        'Slight': [15, 25, '#98aed0'],
        'Mild': [25, 40, '#a5c3df'],
        'Moderate': [40, 55, '#a8d1d9'],
        'Moderately Severe': [55, 70, '#88c1cc'],
        'Severe': [70, 90, '#7ab9b3'],
        'Profound': [90, 120, '#79b7a4']
    }

    for severity in levels.keys():
        min_db = levels[severity][0]
        max_db = levels[severity][1]
        clr = levels[severity][2]

        # Create data points for the curves
        x_values = [0.001, 1000]
        y1_values = [min_db, min_db]
        y2_values = [max_db, max_db]

        # Create PlotDataItem for the curves
        curve1 = pg.PlotDataItem(x=x_values, y=y1_values, pen=pg.mkPen(clr, alpha=255))
        curve2 = pg.PlotDataItem(x=x_values, y=y2_values, pen=pg.mkPen(clr, alpha=255))

        # Add FillBetweenItem
        fill_item = pg.FillBetweenItem(curve1, curve2, brush=pg.mkBrush(clr), pen=None)
        plot_widget.addItem(fill_item)

        # Add text item
        plot_widget.addItem(
            pg.TextItem(severity, color='k', anchor=(0, 1)))


def plot_audiogram(self, audiogram, plot_widget=None, classification=False):
    '''
    Plot the audiogram given an audiogram dict() from parse_audiometry
    Input:
        audiogram [dict] : generate this from the function parse_audiometry().
        plot_widget [PlotWidget] : PlotWidget instance to plot on.
        banana [str] : Choose from [None, 'Left', 'Right', 'Both'].
        classification [bool] : True/False, Whether to plot classification of hearing levels.
    '''
    if plot_widget is None:
        plot_widget = self.fourier_graph

    if classification:
        self.plot_classification(plot_widget)
    if isinstance(audiogram, dict):
        plot_widget.plot(x=list(audiogram['Left'].keys()), y=list(audiogram['Left'].values()), pen=mkPen('b', width=2),
                         symbol='x', name='Left')
        plot_widget.plot(x=list(audiogram['Right'].keys()), y=list(audiogram['Right'].values()),
                         pen=mkPen('r', width=2), symbol='o', symbolBrush='w', name='Right')

    elif isinstance(audiogram, list):
        print("Plotting average audiograms")
        x_left = audiogram[0]['Left'].keys()
        x_right = audiogram[0]['Right'].keys()
        y_left, y_right = [], []
        for n in range(len(audiogram)):
            y_left.append(list(audiogram[n]['Left'].values()))
            y_right.append(list(audiogram[n]['Right'].values()))
        y_left = np.array(y_left)
        y_right = np.array(y_right)
        y_left_mean = y_left.mean(0)
        y_right_mean = y_right.mean(0)
        y_left_stderr = y_left.std(0) / np.sqrt(y_left.shape[0])
        y_right_stderr = y_right.std(0) / np.sqrt(y_right.shape[0])

        plot_widget.addItem(pg.FillBetweenItem(x=x_left, y1=y_left_mean + y_left_stderr, y2=y_left_mean - y_left_stderr,
                                               brush=mkPen('b', alpha=128)))
        plot_widget.plot(x=x_left, y=y_left_mean, pen=mkPen('b', width=2), symbol='x', name='Left')
        plot_widget.addItem(
            pg.FillBetweenItem(x=x_right, y1=y_right_mean + y_right_stderr, y2=y_right_mean - y_right_stderr,
                               brush=mkPen('r', alpha=128)))
        plot_widget.plot(x=x_right, y=y_right_mean, pen=mkPen('r', width=2), symbol='o', symbolBrush='w', name='Right')

    plot_widget.setLogMode(x=True)
    plot_widget.setYRange(-10, 120)
    plot_widget.setXRange(0, 500)

    plot_widget.plotItem.setLabel('bottom', 'Frequency (Hz)')
    plot_widget.plotItem.setLabel('left', 'db')

    plot_widget.enableAutoRange('xy', False)


def toggle_scale_mode(self, classification=True, figname=None, title=''):
    '''
    Create a figure with all of the pure tone audiometry results for xml
    files within a directory [audiometry_dir]
    Inputs:
        audiometry_dir [str]: Path to your audiometry xml files
        banana [None,'Left','Right', or 'Both'] : whether to plot speech banana
        classification [bool] : True/False, whether to show hearing classification.
    '''

    file = self.convert_to_xml()

    plot_widget = self.fourier_graph

    subject = file.split('/')[-1].split('_')[0]
    print(file)
    audiogram = self.parse_audiometry(file)

    self.plot_audiogram(audiogram, plot_widget=plot_widget, classification=classification)
    plot_widget.setTitle(subject)

    # Show the plot widget
    plot_widget.show()


def convert_to_xml(self):
    # Get the file extension
    _, file_extension = os.path.splitext(self.current_file)

    if file_extension.lower() == '.csv':
        # Convert CSV to XML
        df = pd.read_csv(self.current_file)
        xml_file = self.current_file.replace('.csv', '_converted.xml')  # Add suffix
        df.to_xml(xml_file, index=False, parser='etree')  # Use etree parser
        print(f"Converted {self.current_file} to {xml_file}")
        return xml_file

    elif file_extension.lower() == '.wav':
        # Convert WAV to XML
        with wave.open(self.current_file, 'rb') as wav:
            num_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            num_frames = wav.getnframes()

        # Create XML structure
        root = ET.Element("WAVFile")
        ET.SubElement(root, "Channels").text = str(num_channels)
        ET.SubElement(root, "SampleWidth").text = str(sample_width)
        ET.SubElement(root, "FrameRate").text = str(framerate)
        ET.SubElement(root, "NumFrames").text = str(num_frames)

        xml_file = self.current_file.replace('.wav', '_converted.xml')  # Add suffix
        tree = ET.ElementTree(root)
        tree.write(xml_file)
        print(f"Converted {self.current_file} to {xml_file}")
        return xml_file

    else:
        print("Unsupported file type. Please provide a CSV or WAV file.")
        return None