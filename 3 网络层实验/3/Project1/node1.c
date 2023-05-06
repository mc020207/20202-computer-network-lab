#include <stdio.h>

extern struct rtpkt {
	int sourceid;       /* id of sending router sending this pkt */
	int destid;         /* id of router to which pkt being sent
						   (must be an immediate neighbor) */
	int mincost[4];    /* min cost to node 0 ... 3 */
};


extern int TRACE;
extern int YES;
extern int NO;

int connectcosts1[4] = { 1,  0,  1, 999 };
int best1[] = { 0,1,2,-1 };

struct distance_table
{
	int costs[4][4];
} dt1;


/* students to write the following two routines, and maybe some others */


rtinit1()
{
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			dt1.costs[i][j] = 999;
		}
	}
	struct rtpkt tt;
	tt.sourceid = 1;
	for (int j = 0; j < 4; j++) {
		dt1.costs[1][j] = connectcosts1[j];
		tt.mincost[j] = connectcosts1[j];
	}
	for (int j = 0; j < 4; j++) {
		if (j == 1 || connectcosts1[j] == 999) continue;
		tt.destid = j;
		tolayer2(tt);
	}
}


rtupdate1(rcvdpkt)
struct rtpkt* rcvdpkt;

{
	int sid = rcvdpkt->sourceid;
	for (int i = 0; i < 4; i++) {
		dt1.costs[sid][i] = rcvdpkt->mincost[i];
	}
	int change = 0;
	int temp[4];
	for (int j = 0; j < 4; j++) {
		temp[j] = dt1.costs[1][j];
		dt1.costs[1][j] = 999;
		best1[j] = -1;
	}
	for (int j = 0; j < 4; j++) {
		if (j == 1) {
			dt1.costs[j][j] = 0;
			best1[1] = 1;
		}
		for (int k = 0; k < 4; k++) {
			if (connectcosts1[k] + dt1.costs[k][j] < dt1.costs[1][j]) {
				dt1.costs[1][j] = connectcosts1[k] + dt1.costs[k][j];
				best1[j] = k;
			}
		}
	}
	for (int j = 0; j < 4; j++) {
		if (dt1.costs[1][j] != temp[j]) change = 1;
	}
	struct rtpkt tt;
	tt.sourceid = 1;
	if (change) {
		for (int j = 0; j < 4; j++) {
			if (j == 1 || connectcosts1[j] == 999) continue;
			tt.destid = j;
			for (int k = 0; k < 4; k++) {
				if (best1[k] == j) tt.mincost[k] = 999;
				else tt.mincost[k] = dt1.costs[1][k];
			}
			tolayer2(tt);
		}
	}
	printdt1(&dt1);
}


printdt1(dtptr)
struct distance_table* dtptr;

{
	printf("                via     \n");
	printf("   D1 |    0    1     2    3 \n");
	printf("  ----|----------------------\n");
	printf("     0|  %3d   %3d   %3d  %3d\n", dtptr->costs[0][0],
		dtptr->costs[0][1], dtptr->costs[0][2], dtptr->costs[0][3]);
	printf("     1|  %3d   %3d   %3d  %3d\n", dtptr->costs[1][0],
		dtptr->costs[1][1], dtptr->costs[1][2], dtptr->costs[1][3]);
	printf("     2|  %3d   %3d   %3d  %3d\n", dtptr->costs[2][0],
		dtptr->costs[2][1], dtptr->costs[2][2], dtptr->costs[2][3]);
	printf("     3|  %3d   %3d   %3d  %3d\n", dtptr->costs[3][0],
		dtptr->costs[3][1], dtptr->costs[3][2], dtptr->costs[3][3]);

}



linkhandler1(linkid, newcost)
int linkid, newcost;
/* called when cost from 1 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */

{
	connectcosts1[linkid] = newcost;
	int change = 0;
	int temp[4];
	for (int j = 0; j < 4; j++) {
		temp[j] = dt1.costs[1][j];
		dt1.costs[1][j] = 999;
		best1[j] = -1;
	}
	for (int j = 0; j < 4; j++) {
		if (j == 1) {
			dt1.costs[j][j] = 0;
			best1[1] = 1;
		}
		for (int k = 0; k < 4; k++) {
			if (connectcosts1[k] + dt1.costs[k][j] < dt1.costs[1][j]) {
				dt1.costs[1][j] = connectcosts1[k] + dt1.costs[k][j];
				best1[j] = k;
			}
		}
	}
	for (int j = 0; j < 4; j++) {
		if (dt1.costs[1][j] != temp[j]) change = 1;
	}
	struct rtpkt tt;
	tt.sourceid = 1;
	if (change) {
		for (int j = 0; j < 4; j++) {
			if (j == 1 || connectcosts1[j] == 999) continue;
			tt.destid = j;
			for (int k = 0; k < 4; k++) {
				if (best1[k] == j) tt.mincost[k] = 999;
				else tt.mincost[k] = dt1.costs[1][k];
			}
			tolayer2(tt);
		}
	}
}

