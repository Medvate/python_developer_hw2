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


def my_logging_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ValueError as err:
            ERR_LOG.error(f"ValueError [{func.__name__}]: {err}")
            raise err
        except AttributeError as err:
            ERR_LOG.error(f"AttributeError [{func.__name__}]: {err}")
            raise err
        except TypeError as err:
            ERR_LOG.error(f"TypeError [{func.__name__}]: {err}")
            raise err
        except Exception as ex:
            ERR_LOG.error(f"Some Exception [{func.__name__}]: {ex}")
            raise ex

        if 'init' in func.__name__:
            if len(args) <= 2:
                INFO_LOG.info("PatientCollection has been created.")
            else:
                INFO_LOG.info(f"A new patient has been created: {args[0]}.")
        elif 'save' in func.__name__:
            INFO_LOG.info("The patient was successfully saved!")
        elif 'setter' in func.__name__:
            INFO_LOG.info(f"[{func.__name__}]: The change was successful!")
        elif 'check' in func.__name__:
            INFO_LOG.info(f"[{func.__name__}]: The check was successful!")
        else:
            INFO_LOG.info(f"[{func.__name__}]: The function was completed successfully!")

        return result

    return wrapper
