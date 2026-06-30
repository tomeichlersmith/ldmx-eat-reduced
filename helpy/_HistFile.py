import uproot

class HistFile:
    """given a filepath and the name of a ldmx-sw Analyzer,
    access the histograms it created

    For v4.5.1 ldmx-sw and earlier, the analyzer's name was
    repeated as a prefix before the histogram name within
    the TDirectory holding the analyzer's histograms.
    This calss strips off this prefix in order for it to
    appear the same as v4.5.2 ldmx-sw and later histogram
    files."""
    
    def __init__(self, fp, ana, **kwargs):
        """open the passed ROOT file

        Parameters
        ----------
        fp: str, pathlib.Path
            ROOT file to open
        ana: str
            name of analysis within ROOT file
        kwargs: Dict[str,Any]
            key word arguments to be passed to uproot.open
        """

        self._file = uproot.open(fp, **kwargs)
        self._ana = ana
        self._ana_dir = self._file[self._ana]

    def keys(self):
        """get the keys of the objects for the input analysis in this file"""
        return [
            key.removeprefix(f'{self._ana}_').removesuffix(';1')
            for key in self._ana_dir.keys()
        ]

    def get(self, item):
        """get an object from the file without converting it to a hist.Hist"""
        old_style_key = f'{self._ana}_{item}'
        if old_style_key in self._ana_dir:
            return self._ana_dir[old_style_key]
        if item in self._ana_dir:
            return self._ana_dir[item]
        # fall back to whole file so user gets printout of all the keys
        return self._file[item]

    def __getitem__(self, item):
        """get an object and convert it to a hist.Hist"""
        return self.get(item).to_hist()
