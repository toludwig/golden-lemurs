/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { TensorboardComponent } from './tensorboard.component';

describe('TensorboardComponent', () => {
  let component: TensorboardComponent;
  let fixture: ComponentFixture<TensorboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TensorboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TensorboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
