# -*- coding: utf-8 -*-
from scrapy import Spider, http


class ScheduleSpider(Spider):
    name = 'schedule'
    allowed_domains = ['asu.knu.edu.ua']

    def start_requests(self):
        urls = [
            'http://asu.knu.edu.ua/timeTable/group',
        ]
        for url in urls:
            yield http.FormRequest(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'timetable-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info('Saved file %s', filename)

        for faculty in response.xpath('//*[@id="TimeTableForm_faculty"]/option'):
            faculty_id = faculty.xpath('@value').get()
            if not faculty_id:
                continue
            faculty_name = faculty.xpath('text()').get()
            yield {'faculty_id': faculty_id, 'faculty_name': faculty_name}
