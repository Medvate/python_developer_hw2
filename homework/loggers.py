import logging


INFO_LOG = logging.getLogger('info_log')
INFO_LOG.setLevel(logging.INFO)
ERR_LOG = logging.getLogger('err_log')
ERR_LOG.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

good_fh = logging.FileHandler("info.log", mode='a')
good_fh.setFormatter(formatter)
err_fh = logging.FileHandler("errors.log", mode='a')
err_fh.setFormatter(formatter)

INFO_LOG.addHandler(good_fh)
ERR_LOG.addHandler(err_fh)