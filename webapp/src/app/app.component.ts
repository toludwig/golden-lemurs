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
      this.route.url.subscribe(url => {
          console.log(url.join(''));
          let tab = this.tabs.find(tab => this.router.isActive(tab, false));
          this.tabIndex = this.tabs.indexOf(tab);
          if (this.tabIndex == -1)
            this.tabIndex = 0;
      });
  }

  private tabs = ['classify', 'docs', 'tensorboard', 'dashboard', 'data']

  @Output() public tabIndex: number;

  public saveTab(tab: { index: number} ){
      this.tabIndex = tab.index;
      this.router.navigateByUrl(`/${this.tabs[tab.index]}`);
  }
}
