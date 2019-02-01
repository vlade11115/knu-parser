# -*- coding: utf-8 -*-
import scrapy


class ScheduleSpider(scrapy.Spider):
    name = 'schedule'
    allowed_domains = ['asu.knu.edu.ua']

    def start_requests(self):
        urls = [
            'http://asu.knu.edu.ua/timeTable/student',
        ]
        form_data = {
            'TimeTableForm[student]': '-1',  # apparently this hack returns whole schedule.
        }

        for url in urls:
            yield scrapy.http.FormRequest(url=url, callback=self.parse, formdata=form_data, headers=None)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'timetable-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info('Saved file %s', filename)
