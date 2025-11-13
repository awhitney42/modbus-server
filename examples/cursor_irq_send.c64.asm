         *= $7000

         jmp start
         brk       ; SYS(28675)
start    lda $a2
         cmp #$00
         bne skipsend

         lda #$00  ; no filename
         ldx #$00
         ldy #$00
         jsr $ffbd ; setnam

         lda #$05 ; logical file #
         ldx #$02 ; 2 = rs-232 device
         ldy #$00 ; no cmd
         jsr $ffba ; setlfs

         ; c64 rs-232 registers

         lda #$08 ; 1200 baud,8 bits
         sta $0293 ; serial control reg

         lda #$00 ; fullduplex,no parity
         sta $0294 ; serial command reg

         ; open file

         jsr $ffc0 ; open file

         ldx #$05  ; logical file #
         jsr $ffc9 ; chkout
         bcs error

         lda $d3
         jsr $ffd2
         lda $d6
         jsr $ffd2
         lda #$00
         jsr $ffd2 ; send final kludge
         jsr wait
         jmp exit

error    clc
         adc #48
         sta $fc
         lda #$05
         jsr $ffcc ; clrchn
         lda $fc
         jsr $ffd2
         lda #13
         jsr $ffd2

wait     clc
         lda $029d ; tx buffer start
         cmp $029e ; tx buffer end
         bcc wait
         clc
         lda $029b ; rx buffer start
         cmp $029c ; rx buffer end
         bcc wait
done     rts


exit     jsr $ffcc ; clrchn
         lda #$05; logical file #
         jsr $ffc3 ; close
skipsend jmp ($03a0)
install            ; SYS(28791)
         lda $0314
         sta $03a0
         lda $0315
         sta $03a1
         sei
         lda #$00
         sta $0314
         lda #$70
         sta $0315
         cli
         rts
uninstall          ; SYS(28816)
         sei
         lda $03a0
         sta $0314
         lda $03a1
         sta $0315
         cli
         rts
