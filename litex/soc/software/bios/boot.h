#ifndef __BOOT_H
#define __BOOT_H

void serialboot(void);
void netboot(void);
void flashboot(void);
void romboot(void);
void go(char *str);

#endif /* __BOOT_H */
