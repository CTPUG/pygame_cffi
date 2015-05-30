/*
    The contents of this file are all extracted (and dePythoned) from pygame's
    file of the same name.
*/

/* Mac OS X functions to accommodate the fact SDLMain.m is not included */

#include <SDL.h>

#include <Carbon/Carbon.h>
#include <Foundation/Foundation.h>
#include <AppKit/NSApplication.h>
#include <AppKit/NSMenuItem.h>
#include <AppKit/NSMenu.h>
#include <AppKit/NSEvent.h>
#include <Foundation/NSData.h>
#include <AppKit/NSImage.h>

#include <AvailabilityMacros.h>
/* We support OSX 10.6 and below. */
#if __MAC_OS_X_VERSION_MAX_ALLOWED <= 1060
	#define PYGAME_MAC_SCRAP_OLD 1
#endif

struct CPSProcessSerNum
{
	UInt32 lo;
	UInt32 hi;
};
typedef struct CPSProcessSerNum CPSProcessSerNum;

extern OSErr CPSGetCurrentProcess( CPSProcessSerNum *psn);
extern OSErr CPSEnableForegroundOperation( CPSProcessSerNum *psn, UInt32 _arg2, UInt32 _arg3, UInt32 _arg4, UInt32 _arg5);
extern OSErr CPSSetFrontProcess( CPSProcessSerNum *psn);
extern OSErr CPSSetProcessName ( CPSProcessSerNum *psn, const char *processname );

static bool HasInstalledApplication = 0;

static NSString *getApplicationName(void)
{
    const NSDictionary *dict;
    NSString *appName = 0;

    /* Determine the application name */
    dict = (__bridge const NSDictionary *)CFBundleGetInfoDictionary(CFBundleGetMainBundle());
    if (dict)
        appName = [dict objectForKey: @"CFBundleName"];

    if (![appName length])
        appName = [[NSProcessInfo processInfo] processName];

    return appName;
}


const char* WMEnable(void) {
    /* This returns NULL on success, error string on failure. */
	CPSProcessSerNum psn;
    OSErr err;
    const char* nameString;
    NSString* nameNSString;

    err = CPSGetCurrentProcess(&psn);
    if (err != 0) {
    	return "CPSGetCurrentProcess failed";
    }

    nameNSString = getApplicationName();
    nameString = [nameNSString UTF8String];
    CPSSetProcessName(&psn, nameString);

    err = CPSEnableForegroundOperation(&psn,0x03,0x3C,0x2C,0x1103);
    if (err != 0) {
        return "CPSEnableForegroundOperation failed";
    }

    err = CPSSetFrontProcess(&psn);
    if (err != 0) {
        return "CPSSetFrontProcess failed";
    }

    return (const char*) NULL;
}

int RunningFromBundleWithNSApplication(void) {
	if (HasInstalledApplication) {
        return 1;
    }
	CFBundleRef MainBundle = CFBundleGetMainBundle();
	if (MainBundle != NULL) {
		if (CFBundleGetDataPointerForName(MainBundle, CFSTR("NSApp")) != NULL) {
            return 1;
		}
	}
    return 0;
}


//#############################################################################
// Defining the NSApplication class we will use
//#############################################################################
@interface SDLApplication : NSApplication
@end

/* For some reaon, Apple removed setAppleMenu from the headers in 10.4,
 but the method still is there and works. To avoid warnings, we declare
 it ourselves here. */
@interface NSApplication(SDL_Missing_Methods)
- (void)setAppleMenu:(NSMenu *)menu;
@end

@implementation SDLApplication
/* Invoked from the Quit menu item */
- (void)terminate:(id)sender
{
    SDL_Event event;
    event.type = SDL_QUIT;
    SDL_PushEvent(&event);
}
@end

@interface SDLApplicationDelegate : NSObject
@end
@implementation SDLApplicationDelegate
- (BOOL)application:(NSApplication *)theApplication openFile:(NSString *)filename
{
    int posted;

    /* Post the event, if desired */
    posted = 0;
    SDL_Event event;
    event.type = SDL_USEREVENT;
    event.user.code = 0x1000;
    event.user.data1 = SDL_strdup([filename UTF8String]);
    posted = (SDL_PushEvent(&event) > 0);
    return (BOOL)(posted);
}
@end

static void setApplicationMenu(void)
{
    NSMenu *appleMenu;
    NSMenuItem *menuItem;
    NSString *title;
    NSString *appName;

    appName = getApplicationName();
    appleMenu = [[NSMenu alloc] initWithTitle:@""];

    title = [@"About " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(orderFrontStandardAboutPanel:) keyEquivalent:@""];

    [appleMenu addItem:[NSMenuItem separatorItem]];

    title = [@"Hide " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(hide:) keyEquivalent:@"h"];

    menuItem = (NSMenuItem *)[appleMenu addItemWithTitle:@"Hide Others" action:@selector(hideOtherApplications:) keyEquivalent:@"h"];
    [menuItem setKeyEquivalentModifierMask:(NSAlternateKeyMask|NSCommandKeyMask)];

    [appleMenu addItemWithTitle:@"Show All" action:@selector(unhideAllApplications:) keyEquivalent:@""];

    [appleMenu addItem:[NSMenuItem separatorItem]];

    title = [@"Quit " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(terminate:) keyEquivalent:@"q"];

    menuItem = [[NSMenuItem alloc] initWithTitle:@"" action:nil keyEquivalent:@""];
    [menuItem setSubmenu:appleMenu];
    [[NSApp mainMenu] addItem:menuItem];

    [NSApp setAppleMenu:appleMenu];

    [appleMenu release];
    [menuItem release];
}

static void setupWindowMenu(void)
{
    NSMenu      *windowMenu;
    NSMenuItem  *windowMenuItem;
    NSMenuItem  *menuItem;

    windowMenu = [[NSMenu alloc] initWithTitle:@"Window"];

    menuItem = [[NSMenuItem alloc] initWithTitle:@"Minimize" action:@selector(performMiniaturize:) keyEquivalent:@"m"];
    [windowMenu addItem:menuItem];
    [menuItem release];

    windowMenuItem = [[NSMenuItem alloc] initWithTitle:@"Window" action:nil keyEquivalent:@""];
    [windowMenuItem setSubmenu:windowMenu];
    [[NSApp mainMenu] addItem:windowMenuItem];

    [NSApp setWindowsMenu:windowMenu];

    [windowMenu release];
    [windowMenuItem release];
}


int InstallNSApplication(void) {
    // TODO: Icon setup stuff.
    char* icon_data = NULL;
    int data_len = 0;
    SDLApplicationDelegate *sdlApplicationDelegate = NULL;

    NSAutoreleasePool	*pool = [[NSAutoreleasePool alloc] init];

    [SDLApplication sharedApplication];

    if (0) {
        NSData *image_data = [NSData dataWithBytes:icon_data length:data_len];
	    NSImage *icon_img = [[NSImage alloc] initWithData:image_data];
	    if (icon_img != NULL) {
	    	[NSApp setApplicationIconImage:icon_img];
	    }
    }

    [NSApp setMainMenu:[[NSMenu alloc] init]];
    setApplicationMenu();
    setupWindowMenu();

    [NSApp finishLaunching];
    [NSApp updateWindows];
    [NSApp activateIgnoringOtherApps:true];

    HasInstalledApplication = 1;

    /* Create SDLApplicationDelegate and make it the app delegate */
    sdlApplicationDelegate = [[SDLApplicationDelegate alloc] init];
    [NSApp setDelegate:sdlApplicationDelegate];

	return 1;
}
