import { Component, EventEmitter, Output, ViewChild, ViewEncapsulation } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { html } from 'd3';

@Component({
  selector: 'app-docs',
  templateUrl: './docs.component.html',
  styleUrls: ['./docs.component.css'],
  encapsulation: ViewEncapsulation.None
})
export class DocsComponent {
  @ViewChild('docs') docs;

  constructor(private route: ActivatedRoute) {
    route.params.subscribe((params) => {
      let target = params['page']
      let url = `/assets/docs/${target}.md.html`;
      html(url, doc => {
        let elem = this.docs.nativeElement;
        while (elem.firstChild) elem.removeChild(elem.firstChild);
        elem.appendChild(doc);
        // var script = document.createElement("script");
        // script.type = "text/javascript";
        // script.src = "http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML";
        // document.getElementsByTagName("head")[0].appendChild(script);
      });
    });
  }
  //   let req = new XMLHttpRequest();
  //   req.addEventListener("load", () => {
  //       this.content.emit(req.responseText);
  //   });
  //   req.send();
  // });


  //@Output() content = new EventEmitter<string>();

}
