import { Component, Output } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Github classifier by golden lemurs';
  subtitle = 'InformatiCup 2016';

  public constructor(private router: Router, private route: ActivatedRoute) {
      // select tab according to current route
      this.router.events.subscribe( () => {
          let tab = this.tabs.find(tab => this.router.isActive(tab, false));
          this.tabIndex = this.tabs.indexOf(tab);
          if (this.tabIndex == -1)
            this.tabIndex = 0;
      });
  }

  private tabs = ['classify', 'docs', 'tensorboard', 'data']
  private entries = ['classify', 'docs/intro', 'tensorboard', 'data'];

  @Output() public tabIndex: number;

  public saveTab(tab: { index: number} ){
      // change route according to selected tab
      this.tabIndex = tab.index;
      this.router.navigateByUrl(`/${this.entries[tab.index]}`);
  }
}
