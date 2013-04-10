//
//  TrackSearchViewController.h
//  DJPi
//
//  Created by Chris Vanderschuere on 3/28/13.
//  Copyright (c) 2013 CDVConcepts. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface TrackSearchViewController : UIViewController <UISearchBarDelegate, UITableViewDelegate,UITableViewDataSource>
@property (weak, nonatomic) IBOutlet UISearchBar *searchBar;
@property (weak, nonatomic) IBOutlet UITableView *results;

@property (nonatomic, strong) NSURL* selectedTrackURL;

@end
