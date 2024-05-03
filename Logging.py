# --- Imports
import Params as P


# --- Defs
def frameLog(drops):  # Logging every frame
    info = f"\nFrame: #{P.frameCount:<10} Drop count: {len(drops):<10}\n"
    P.logFrame.write(info)

    start_line = " Area in PX  |  Area in MM  | Left Offset | Top Offset\n"
    P.logFrame.write(start_line)

    for x in range(0, len(drops)):
        area_px = drops[x].areaPX[0]
        area_mm = drops[x].areaMM[0]
        left = drops[x].left[0]
        top = drops[x].top[0]

        drop_info = str(area_px).rjust(10) + "px | " \
                    + str(area_mm).rjust(10) + "mm | " \
                    + str(left).rjust(9) + "px | " \
                    + str(top).rjust(9) + 'px \n'

        P.logFrame.write(drop_info)

def queueLog(length):

    P.threadCount += 1

    info = f"\nLength: {length:<10} frames Drops: {len(P.queueDrops)}\n"
    P.logQueue.write(info)

    start_line = "Thread | Avg. Area in PX | Avg. Area in MM | Offset\n"
    P.logQueue.write(start_line)

    for x in range(0, len(P.queueDrops)):
        area_px = P.queueDrops[x].getAreaPX()
        area_mm = P.queueDrops[x].getAreaMM()
        left = P.queueDrops[x].getLeft()

        drop_info = str(P.threadCount).ljust(6) + " | " \
                    + str(area_px).rjust(13) + "px | " \
                    + str(area_mm).rjust(13) + "mm | " \
                    + str(left).rjust(5) + "px\n"

        P.logQueue.write(drop_info)

    P.queueDrops = []
    P.inactiveDrops = 0