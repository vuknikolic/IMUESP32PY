import pygame
import threading
from serial_receiver import SerialReceiver
from packet_processor import PacketProcessor

SERIAL_PORT = '/dev/tty.usbmodem14201'
BAUD_RATE = 115200
SYNC_BYTE = b'\xAA'
RAW_DATA_LENGTH = 16

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IMUESP32PY")
font = pygame.font.Font(None, 26)
running = True
global processor

# fiksni prealocirani ciklicni bafer
MAX_BUFFER_LENGTH = 100
buffer_index = 0  # zajednicki index za sve bafere

# popuni ih nulama
accel_x_buffer = [0] * MAX_BUFFER_LENGTH
accel_y_buffer = [0] * MAX_BUFFER_LENGTH
accel_z_buffer = [0] * MAX_BUFFER_LENGTH
gyro_x_buffer  = [0] * MAX_BUFFER_LENGTH
gyro_y_buffer  = [0] * MAX_BUFFER_LENGTH
gyro_z_buffer  = [0] * MAX_BUFFER_LENGTH

# scale faktor ±2g za akcelerometar, ±250 dps za ziroskop
accel_scale = HEIGHT/3 / 4.0    # ±2g => opseg je puta 2
gyro_scale  = HEIGHT/3 / 500.0   # ±250 dps => opseg je puta 2

# farba
colors = {
    'accel_x': (255, 0, 0),     
    'accel_y': (0, 255, 0),     
    'accel_z': (0, 0, 255),     
    'gyro_x':  (255, 0, 0),   
    'gyro_y':  (0, 255, 0),   
    'gyro_z':  (0, 0, 255)    
}

def rdata(packet: bytes):
    global processor, screen, font, buffer_index
    processor.process_packet(packet)
    
    # svaka nova vrednost prepisuje najstariju
    accel_x_buffer[buffer_index] = processor.accel_x_g
    accel_y_buffer[buffer_index] = processor.accel_y_g
    accel_z_buffer[buffer_index] = processor.accel_z_g
    gyro_x_buffer[buffer_index]  = processor.gyro_x_dps
    gyro_y_buffer[buffer_index]  = processor.gyro_y_dps
    gyro_z_buffer[buffer_index]  = processor.gyro_z_dps
    buffer_index = (buffer_index + 1) % MAX_BUFFER_LENGTH

    # napravi nove bafere od indeksa pa dopuni sa pre indexa
    ordered_accel_x = accel_x_buffer[buffer_index:] + accel_x_buffer[:buffer_index]
    ordered_accel_y = accel_y_buffer[buffer_index:] + accel_y_buffer[:buffer_index]
    ordered_accel_z = accel_z_buffer[buffer_index:] + accel_z_buffer[:buffer_index]
    ordered_gyro_x  = gyro_x_buffer[buffer_index:]  + gyro_x_buffer[:buffer_index]
    ordered_gyro_y  = gyro_y_buffer[buffer_index:]  + gyro_y_buffer[:buffer_index]
    ordered_gyro_z  = gyro_z_buffer[buffer_index:]  + gyro_z_buffer[:buffer_index]

    screen.fill((20, 20, 20))

    # legenda
    text = font.render("Accel", True, (255, 255, 255))
    screen.blit(text, ((10 ) // 2, 35))
    text = font.render("Gyro", True, (255, 255, 255))
    screen.blit(text, ((10 ) // 2, 335))
    text = font.render("X", True, (255, 0, 0))
    screen.blit(text, ((1500) // 2, 5))
    text = font.render("Y", True, (0, 255, 0))
    screen.blit(text, ((1530) // 2, 5))
    text = font.render("Z", True, (0, 0, 255))
    screen.blit(text, ((1560) // 2, 5))

    # granicne linije
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4],[WIDTH,HEIGHT/4]], 2)
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4*3],[WIDTH,HEIGHT/4*3]], 2)
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4-accel_scale*2],[WIDTH,HEIGHT/4-accel_scale*2]], 2)
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4+accel_scale*2],[WIDTH,HEIGHT/4+accel_scale*2]], 2)
    pygame.draw.lines(screen, (50,50,50), False, [[0,HEIGHT/4-accel_scale],[WIDTH,HEIGHT/4-accel_scale]], 2)
    pygame.draw.lines(screen, (50,50,50), False, [[0,HEIGHT/4+accel_scale],[WIDTH,HEIGHT/4+accel_scale]], 2)
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4*3-gyro_scale*250],[WIDTH,HEIGHT/4*3-gyro_scale*250]], 2)
    pygame.draw.lines(screen, (100,100,100), False, [[0,HEIGHT/4*3+gyro_scale*250],[WIDTH,HEIGHT/4*3+gyro_scale*250]], 2)


    x_spacing = WIDTH / (MAX_BUFFER_LENGTH - 1)
    
    # crtaj liniju za jedan bafer
    def draw_line(ordered_data, baseline, scale, color):
        points = []
        for i, value in enumerate(ordered_data):
            x = i * x_spacing
            y = baseline - (value * scale)
            points.append((x, y))
        pygame.draw.lines(screen, color, False, points, 2)
    
    # crtaj grafike
    draw_line(ordered_accel_x, HEIGHT/4, accel_scale, colors['accel_x'])
    draw_line(ordered_accel_y, HEIGHT/4, accel_scale, colors['accel_y'])
    draw_line(ordered_accel_z, HEIGHT/4, accel_scale, colors['accel_z'])
    draw_line(ordered_gyro_x,  HEIGHT/4*3, gyro_scale,  colors['gyro_x'])
    draw_line(ordered_gyro_y,  HEIGHT/4*3, gyro_scale,  colors['gyro_y'])
    draw_line(ordered_gyro_z,  HEIGHT/4*3, gyro_scale,  colors['gyro_z'])
    
    pygame.display.flip()

def main():
    global processor, running
    receiver = SerialReceiver(SERIAL_PORT, BAUD_RATE, SYNC_BYTE, RAW_DATA_LENGTH)
    processor = PacketProcessor()
    receiver.set_packet_callback(rdata)
    
    # serial receiver u posebnom thread-u
    recv_thread = threading.Thread(target=receiver.start, daemon=True)
    recv_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        pygame.time.wait(1)
    
    receiver.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
