import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule, Routes } from '@angular/router';

import { MaterialModule } from '@angular/material';

import { AppComponent } from './app.component';
import { ClassifyComponent} from './classify/classify.component';
import { DocsComponent } from './docs/docs.component';
import { NetworkComponent } from './network/network.component';

// const routes = [
//     { path: '', pathMatch: 'full', redirectTo: 'classify'},
//     { path: 'classify', component: ClassifyComponent},
//     { path: 'network', component: NetworkComponent},
//     { path: 'docs', component: DocsComponent}
// ];

@NgModule({
  declarations: [
    AppComponent,
    ClassifyComponent,
    DocsComponent,
    NetworkComponent],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    // RouterModule.forRoot(routes),
    MaterialModule.forRoot()
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
