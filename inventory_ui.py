import pygame

HELP1 = "인벤토리: ↑/↓ 선택, ENTER=사용/장착, U=해제, DEL=버리기, ESC=닫기"
HELP2 = "장비 슬롯: [W]무기 [A]방어구 [S]장신구 [R]룬 → U로 해제"

def open_inventory(screen, font, player):
    idx = 0
    running = True
    while running:
        screen.fill((18, 18, 22))
        screen.blit(font.render(HELP1, True, (255,255,255)), (40, 40))
        screen.blit(font.render(HELP2, True, (200,200,200)), (40, 70))

        # 장비 상태
        y_equ = 110
        for slot in ("weapon","armor","accessory","rune"):
            eq = player.equipment.get(slot)
            line = f"{slot.upper():9}: {eq['name'] if eq else '-'}"
            screen.blit(font.render(line, True, (255,220,120)), (40, y_equ))
            y_equ += 30

        # 아이템 리스트 시작 위치를 '장비 블럭 아래'로 이동(겹침 방지)
        start_y = y_equ + 10
        if not player.inventory:
            screen.blit(font.render("(인벤토리 비어 있음)", True, (180,180,180)), (40, start_y))
        else:
            for i, item in enumerate(player.inventory):
                mark = "▶ " if i == idx else "  "
                name = item.get("name","?")
                desc = item.get("desc","")
                color = (255,255,255) if i != idx else (120,255,120)
                screen.blit(font.render(f"{mark}{name}  {desc}", True, color), (40, start_y + i*28))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    if player.inventory:
                        idx = (idx + 1) % len(player.inventory)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if player.inventory:
                        idx = (idx - 1) % len(player.inventory)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if player.inventory:
                        it = player.inventory[idx]
                        if it.get("type") == "consumable":
                            player.use_consumable(idx)
                            idx = min(idx, len(player.inventory)-1)
                        elif it.get("type") in ("weapon","armor","accessory","rune"):
                            player.equip_item(idx)
                            idx = min(idx, len(player.inventory)-1)
                elif event.key == pygame.K_u:
                    if player.inventory:
                        it = player.inventory[idx]
                        slot = it.get("slot")
                        if slot and player.equipment.get(slot):
                            player.unequip(slot)
                elif event.key == pygame.K_DELETE:
                    if player.inventory:
                        player.inventory.pop(idx)
                        idx = min(idx, len(player.inventory)-1)
                elif event.key == pygame.K_ESCAPE:
                    return
