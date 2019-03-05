from horus.engine.scan.ciclop_scan import CiclopScan

#####SETUP#####
print("Setting up scanner...", end='')
scanner = CiclopScan()
scanner._initialize()
scanner.set_capture_texture(False)

print("Done!")

# scanner.driver.board.connect()
