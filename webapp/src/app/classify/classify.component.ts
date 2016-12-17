import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-classify',
  templateUrl: './classify.component.html',
  styleUrls: ['./classify.component.css']
})
export class ClassifyComponent implements OnInit {

  input = 'Enter a github repo url';
  action = 'Classify me!';
  constructor() { }

  ngOnInit() {
  }

}
