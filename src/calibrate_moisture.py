import time

import board

from lib.moisture_sensor import MoistureSensor


MOISTURE_ANALOG_PIN = board.GP26
SAMPLE_COUNT = 20
SAMPLE_INTERVAL_SEC = 0.1


def wait_for_enter(message):
    print("")
    input(message)


def sample_raw(
    sensor, label, sample_count=SAMPLE_COUNT, interval_sec=SAMPLE_INTERVAL_SEC
):
    total = 0
    minimum = None
    maximum = None

    print("{} の測定を開始します".format(label))
    for index in range(sample_count):
        raw = sensor.read_raw()
        total += raw
        if minimum is None or raw < minimum:
            minimum = raw
        if maximum is None or raw > maximum:
            maximum = raw

        print("  sample {:02d}: {}".format(index + 1, raw))
        time.sleep(interval_sec)

    average = int(total / sample_count)
    print(
        "{} の測定結果: avg={} min={} max={}".format(label, average, minimum, maximum)
    )
    return average


def print_result(dry_raw, wet_raw):
    midpoint = (dry_raw + wet_raw) / 2

    print("")
    print("Calibration result")
    print("DRY_RAW = {}".format(dry_raw))
    print("WET_RAW = {}".format(wet_raw))
    print("参考: dry/wet の中間値 = {:.1f}".format(midpoint))
    print("")
    print("src/code.py の設定例")
    print("DRY_RAW = {}".format(dry_raw))
    print("WET_RAW = {}".format(wet_raw))


def main():
    sensor = MoistureSensor(MOISTURE_ANALOG_PIN)

    print("Soil moisture calibration tool")
    print("Thonny から実行し、表示に従って Enter を押してください")
    print("使用ピン: {}".format(MOISTURE_ANALOG_PIN))
    print("1回あたり {} サンプルを平均化します".format(SAMPLE_COUNT))

    try:
        wait_for_enter("乾いた土、または空気中にセンサーを置いて Enter > ")
        dry_raw = sample_raw(sensor, "DRY_RAW")

        wait_for_enter(
            "湿った土、または十分に水を含んだ状態にセンサーを置いて Enter > "
        )
        wet_raw = sample_raw(sensor, "WET_RAW")

        if dry_raw <= wet_raw:
            print("")
            print("注意: DRY_RAW が WET_RAW 以下です")
            print("配線、センサーの向き、測定条件を見直してください")

        print_result(dry_raw, wet_raw)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        sensor.deinit()


main()
