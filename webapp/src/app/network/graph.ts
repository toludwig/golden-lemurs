import * as d3 from 'd3';
import * as ejs from 'ejs';

export function constructGraph(svg, data, templateData) {
  plotLevel(svg, data, 1, templateData);
}

function plotLevel(parent, data, level, templateData) {
  parent.selectAll(`.level_${level}`)
    .data(data.children)
    .enter().append("g")
    .each(function(d: any, i) {
      let elem = this;
      d3.request(`/assets/${d.template}.svg`)
        .mimeType("application/json")
        .response(xhr => xhr.responseText)
        .get(function(template) {
          elem.innerHTML = ejs.render(template, templateData);
          if (d.children)
              plotLevel(d3.select(elem), d, level + 1, templateData);
        });
    });
}
