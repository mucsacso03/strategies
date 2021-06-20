from system_components.run_timer import cmd_output_end, cmd_output_start

def make_email_message(signals_sum):
    start_time = cmd_output_start('Detecting...')
    trendirany = []
    korrekcio = []
    for signals in signals_sum:
        for signal in signals:
            if signal.orientation == signal.trend and signal.orientation == signal.sector_trend:

                trendirany.append(signal)
            else:
                korrekcio.append(signal)

    with open('previous_mail.txt', "r") as file:
        previous_signals = file.read()

    new_signal = False
    str_message = "Trendiranyu dimbesdombos\n\n"
    str_trendirany = ""
    for signal in trendirany:
        signal_str = signal.instrument + " - " + signal.timeframe.name + ": " \
                     + signal.orientation.name + "\t\t|\t\t" + str(signal.peak_timestamp) + " - " + str(signal.value) \
                     + "\n"
        if signal_str not in previous_signals:
            str_trendirany = str_trendirany + signal_str
            new_signal = True

    print("\nMail content:\n\n" + str_trendirany)

    with open('previous_mail.txt', "a+") as file:
        file.write(str_trendirany)

    file.close()

    str_message = str_message + str_trendirany

    cmd_output_end(start_time)

    # str_korrekcio = "Korrekcios dimbesdombos\n\n"
    # for signal in korrekcio:
    #     str_korrekcio = str_korrekcio + signal.instrument + " - " + signal.timeframe.name + ": " \
    #                     + signal.orientation.name + " " + str(signal.peak_timestamp) + " " + str(signal.value) \
    #                     + "\n"
    # print(str_korrekcio)
    return str_message, new_signal